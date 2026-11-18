/**
 * MiniKVS: High-Performance Embedded Key-Value Storage Engine
 * Level 2 Capstone Project Implementation
 * Language: C99 / C11
 */

#include "mini_kvs.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <assert.h>

#define INITIAL_BUCKETS 64
#define HASH_SEED 5381

// Tracked Allocator for Memory Verification
static size_t g_kvs_allocated_bytes = 0;

static void* kvs_malloc(size_t sz) {
    if (sz == 0) return NULL;
    size_t *block = (size_t *)malloc(sizeof(size_t) + sz);
    if (!block) return NULL;
    *block = sz;
    g_kvs_allocated_bytes += sz;
    return (void *)(block + 1);
}

static void kvs_free(void *ptr) {
    if (!ptr) return;
    size_t *block = ((size_t *)ptr) - 1;
    g_kvs_allocated_bytes -= *block;
    free(block);
}

static char* kvs_strdup(const char *s) {
    if (!s) return NULL;
    size_t len = strlen(s);
    char *copy = (char *)kvs_malloc(len + 1);
    if (copy) {
        memcpy(copy, s, len + 1);
    }
    return copy;
}

// In-Memory Hash Table Node
typedef struct HashNode {
    KVS_IndexEntry entry;
    struct HashNode *next;
} HashNode;

// Engine State
struct KVS_Engine {
    FILE *file;
    char *filepath;
    HashNode **buckets;
    size_t bucket_count;
    size_t total_keys;
};

// DJB2 Hash Algorithm
static uint32_t hash_djb2(const char *str) {
    uint32_t hash = HASH_SEED;
    int c;
    while ((c = (unsigned char)*str++)) {
        hash = ((hash << 5) + hash) + c; // hash * 33 + c
    }
    return hash;
}

// Calculate simple XOR checksum across buffer
static uint8_t compute_checksum(const void *data, size_t len) {
    const uint8_t *p = (const uint8_t *)data;
    uint8_t csum = 0;
    for (size_t i = 0; i < len; ++i) {
        csum ^= p[i];
    }
    return csum;
}

// Internal Index Operations
static HashNode* find_node(KVS *kvs, const char *key, size_t *out_bucket) {
    uint32_t h = hash_djb2(key);
    size_t b = h % kvs->bucket_count;
    if (out_bucket) *out_bucket = b;

    HashNode *curr = kvs->buckets[b];
    while (curr) {
        if (strcmp(curr->entry.key, key) == 0) {
            return curr;
        }
        curr = curr->next;
    }
    return NULL;
}

static void index_put(KVS *kvs, const char *key, uint64_t offset, uint32_t val_len) {
    size_t b;
    HashNode *existing = find_node(kvs, key, &b);
    if (existing) {
        existing->entry.file_offset = offset;
        existing->entry.val_len = val_len;
        return;
    }

    HashNode *node = (HashNode *)kvs_malloc(sizeof(HashNode));
    assert(node != NULL);
    node->entry.key = kvs_strdup(key);
    node->entry.file_offset = offset;
    node->entry.val_len = val_len;
    node->next = kvs->buckets[b];
    kvs->buckets[b] = node;
    kvs->total_keys++;
}

static void index_delete(KVS *kvs, const char *key) {
    size_t b;
    uint32_t h = hash_djb2(key);
    b = h % kvs->bucket_count;

    HashNode *curr = kvs->buckets[b];
    HashNode *prev = NULL;

    while (curr) {
        if (strcmp(curr->entry.key, key) == 0) {
            if (prev) {
                prev->next = curr->next;
            } else {
                kvs->buckets[b] = curr->next;
            }
            kvs_free(curr->entry.key);
            kvs_free(curr);
            kvs->total_keys--;
            return;
        }
        prev = curr;
        curr = curr->next;
    }
}

// Rebuild index by scanning log from start to finish
static void recover_from_disk(KVS *kvs) {
    fseek(kvs->file, 0, SEEK_SET);
    KVS_RecordHeader hdr;

    while (fread(&hdr, sizeof(KVS_RecordHeader), 1, kvs->file) == 1) {
        if (hdr.magic != KVS_MAGIC_BYTE) {
            // Unrecognized or corrupted block; stop recovery
            break;
        }

        char *key_buf = (char *)kvs_malloc(hdr.key_len + 1);
        if (fread(key_buf, 1, hdr.key_len, kvs->file) != hdr.key_len) {
            kvs_free(key_buf);
            break;
        }
        key_buf[hdr.key_len] = '\0';

        // Read or skip value
        uint64_t val_offset = ftell(kvs->file);
        fseek(kvs->file, hdr.val_len, SEEK_CUR);

        // Read checksum byte
        uint8_t csum;
        if (fread(&csum, 1, 1, kvs->file) != 1) {
            kvs_free(key_buf);
            break;
        }

        if (hdr.flags & KVS_FLAG_TOMBSTONE) {
            index_delete(kvs, key_buf);
        } else {
            index_put(kvs, key_buf, val_offset, hdr.val_len);
        }
        kvs_free(key_buf);
    }
}

// Public API Implementation
KVS* kvs_open(const char *filepath) {
    if (!filepath) return NULL;

    KVS *kvs = (KVS *)kvs_malloc(sizeof(KVS));
    if (!kvs) return NULL;

    kvs->filepath = kvs_strdup(filepath);
    kvs->bucket_count = INITIAL_BUCKETS;
    kvs->total_keys = 0;
    kvs->buckets = (HashNode **)kvs_malloc(kvs->bucket_count * sizeof(HashNode *));
    memset(kvs->buckets, 0, kvs->bucket_count * sizeof(HashNode *));

    // Open existing or create new file in update binary mode
    kvs->file = fopen(filepath, "a+b");
    if (!kvs->file) {
        kvs_free(kvs->buckets);
        kvs_free(kvs->filepath);
        kvs_free(kvs);
        return NULL;
    }

    // Replay log to build in-memory index
    recover_from_disk(kvs);

    return kvs;
}

KVS_Status kvs_put(KVS *kvs, const char *key, const char *val) {
    if (!kvs || !key || !val) return KVS_ERR_INVALID;

    size_t klen = strlen(key);
    size_t vlen = strlen(val);
    if (klen > 65535 || vlen > 10000000) return KVS_ERR_INVALID;

    // Seek to EOF for appending
    fseek(kvs->file, 0, SEEK_END);
    uint64_t record_start = ftell(kvs->file);

    KVS_RecordHeader hdr;
    hdr.magic = KVS_MAGIC_BYTE;
    hdr.flags = KVS_FLAG_ACTIVE;
    hdr.timestamp = (uint64_t)time(NULL);
    hdr.key_len = (uint16_t)klen;
    hdr.val_len = (uint32_t)vlen;

    // Compute checksum over header + key + val
    uint8_t csum = compute_checksum(&hdr, sizeof(KVS_RecordHeader));
    csum ^= compute_checksum(key, klen);
    csum ^= compute_checksum(val, vlen);

    // Write header, key, value, checksum
    if (fwrite(&hdr, sizeof(KVS_RecordHeader), 1, kvs->file) != 1 ||
        fwrite(key, 1, klen, kvs->file) != klen ||
        fwrite(val, 1, vlen, kvs->file) != vlen ||
        fwrite(&csum, 1, 1, kvs->file) != 1) {
        return KVS_ERR_IO;
    }

    fflush(kvs->file);

    // In-memory index records the exact byte offset where the VALUE starts
    uint64_t val_offset = record_start + sizeof(KVS_RecordHeader) + klen;
    index_put(kvs, key, val_offset, (uint32_t)vlen);

    return KVS_OK;
}

KVS_Status kvs_get(KVS *kvs, const char *key, char *out_val_buf, size_t buf_capacity) {
    if (!kvs || !key || !out_val_buf || buf_capacity == 0) return KVS_ERR_INVALID;

    HashNode *node = find_node(kvs, key, NULL);
    if (!node) return KVS_ERR_NOT_FOUND;

    if (node->entry.val_len >= buf_capacity) {
        return KVS_ERR_MEM; // Buffer too small for complete value
    }

    // Direct Random Access Seek directly to the value on disk!
    if (fseek(kvs->file, (long)node->entry.file_offset, SEEK_SET) != 0) {
        return KVS_ERR_IO;
    }

    size_t read_bytes = fread(out_val_buf, 1, node->entry.val_len, kvs->file);
    if (read_bytes != node->entry.val_len) {
        return KVS_ERR_IO;
    }

    out_val_buf[node->entry.val_len] = '\0'; // Guarantee null termination
    return KVS_OK;
}

KVS_Status kvs_delete(KVS *kvs, const char *key) {
    if (!kvs || !key) return KVS_ERR_INVALID;

    HashNode *node = find_node(kvs, key, NULL);
    if (!node) return KVS_ERR_NOT_FOUND;

    // Append Tombstone Record to Disk
    fseek(kvs->file, 0, SEEK_END);
    size_t klen = strlen(key);

    KVS_RecordHeader hdr;
    hdr.magic = KVS_MAGIC_BYTE;
    hdr.flags = KVS_FLAG_TOMBSTONE;
    hdr.timestamp = (uint64_t)time(NULL);
    hdr.key_len = (uint16_t)klen;
    hdr.val_len = 0;

    uint8_t csum = compute_checksum(&hdr, sizeof(KVS_RecordHeader)) ^ compute_checksum(key, klen);

    if (fwrite(&hdr, sizeof(KVS_RecordHeader), 1, kvs->file) != 1 ||
        fwrite(key, 1, klen, kvs->file) != klen ||
        fwrite(&csum, 1, 1, kvs->file) != 1) {
        return KVS_ERR_IO;
    }

    fflush(kvs->file);

    // Remove from in-memory index
    index_delete(kvs, key);
    return KVS_OK;
}

KVS_Status kvs_close(KVS *kvs) {
    if (!kvs) return KVS_ERR_INVALID;

    if (kvs->file) {
        fclose(kvs->file);
        kvs->file = NULL;
    }

    // Free all hash table buckets
    for (size_t b = 0; b < kvs->bucket_count; ++b) {
        HashNode *curr = kvs->buckets[b];
        while (curr) {
            HashNode *tmp = curr->next;
            kvs_free(curr->entry.key);
            kvs_free(curr);
            curr = tmp;
        }
    }
    kvs_free(kvs->buckets);
    kvs_free(kvs->filepath);
    kvs_free(kvs);

    return KVS_OK;
}

size_t kvs_get_key_count(const KVS *kvs) {
    return kvs ? kvs->total_keys : 0;
}

size_t kvs_get_active_memory(void) {
    return g_kvs_allocated_bytes;
}

#ifdef MINI_KVS_STANDALONE
int main(void) {
    printf("=== MiniKVS Standalone Self-Test ===\n");
    const char *db_path = "test_standalone.kvs";
    remove(db_path);

    KVS *kvs = kvs_open(db_path);
    assert(kvs != NULL);

    kvs_put(kvs, "user:101", "{\"name\": \"Aditi\", \"tier\": \"gold\"}");
    kvs_put(kvs, "user:102", "{\"name\": \"Vikram\", \"tier\": \"silver\"}");

    char buf[128];
    assert(kvs_get(kvs, "user:101", buf, sizeof(buf)) == KVS_OK);
    printf("Retrieved user:101 -> %s\n", buf);

    kvs_close(kvs);
    printf("Active memory after close: %zu bytes (Leak balanced!)\n", kvs_get_active_memory());
    assert(kvs_get_active_memory() == 0);

    remove(db_path);
    printf("=== Self-Test Passed Cleanly ===\n");
    return 0;
}
#endif
