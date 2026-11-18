#ifndef MINI_KVS_H
#define MINI_KVS_H

/**
 * MiniKVS: High-Performance Embedded Key-Value Storage Engine
 * Level 2 Capstone Project
 * Language: C99 / C11
 */

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Status Codes
typedef enum {
    KVS_OK = 0,
    KVS_ERR_NOT_FOUND = -1,
    KVS_ERR_IO = -2,
    KVS_ERR_CORRUPT = -3,
    KVS_ERR_MEM = -4,
    KVS_ERR_INVALID = -5
} KVS_Status;

// Record Wire Format Header (Packed)
#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;       // 0x5A
    uint8_t  flags;       // Bit 0: 0 = Active, 1 = Tombstone (Deleted)
    uint64_t timestamp;   // Milliseconds unix epoch
    uint16_t key_len;     // Length of key string (excluding null)
    uint32_t val_len;     // Length of value string (excluding null)
} KVS_RecordHeader;
#pragma pack(pop)

#define KVS_MAGIC_BYTE 0x5A
#define KVS_FLAG_ACTIVE    0x00
#define KVS_FLAG_TOMBSTONE 0x01

// In-Memory Index Entry
typedef struct {
    char *key;
    uint64_t file_offset;
    uint32_t val_len;
} KVS_IndexEntry;

// Opaque KVS Engine Handle
typedef struct KVS_Engine KVS;

// Public API
KVS*       kvs_open(const char *filepath);
KVS_Status kvs_put(KVS *kvs, const char *key, const char *val);
KVS_Status kvs_get(KVS *kvs, const char *key, char *out_val_buf, size_t buf_capacity);
KVS_Status kvs_delete(KVS *kvs, const char *key);
KVS_Status kvs_close(KVS *kvs);

// Diagnostic & Introspection
size_t     kvs_get_key_count(const KVS *kvs);
size_t     kvs_get_active_memory(void);

#ifdef __cplusplus
}
#endif

#endif // MINI_KVS_H
