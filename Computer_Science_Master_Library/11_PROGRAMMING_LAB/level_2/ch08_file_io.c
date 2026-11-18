/*
 * Chapter 08 Lab: File I/O, Streams, and Persistence in C
 * Language: C99 / C11
 *
 * Demonstrates:
 * 1. Buffered text file creation and reading line-by-line via fgets().
 * 2. Binary struct serialization and deserialization via fread() / fwrite().
 * 3. Random access seek calculations (fseek/ftell).
 * 4. Stream error detection via ferror().
 */

#include <stdio.h>
#include <stdint.h>
#include <string.h>

#pragma pack(push, 1)
typedef struct {
    uint32_t record_id;
    char key[24];
    double value;
} TelemetryPoint;
#pragma pack(pop)

int main(void) {
    const char *text_file = "lab_text.txt";
    const char *bin_file = "lab_records.bin";

    printf("=== Demonstration 1: Buffered Text File Operations ===\n");
    FILE *ft = fopen(text_file, "w");
    if (!ft) {
        perror("Failed to create text file");
        return 1;
    }
    fprintf(ft, "Sensor Node Alpha\nTemperature: 28.5 C\nStatus: ONLINE\n");
    fclose(ft);

    // Read back
    ft = fopen(text_file, "r");
    if (ft) {
        char line[128];
        int line_num = 1;
        while (fgets(line, sizeof(line), ft)) {
            printf("  Line %d: %s", line_num++, line);
        }
        fclose(ft);
    }

    printf("\n=== Demonstration 2: Binary Struct Persistence ===\n");
    TelemetryPoint points[3] = {
        {101, "cpu_usage", 45.2},
        {102, "mem_usage", 68.7},
        {103, "disk_io",   12.4}
    };

    FILE *fb = fopen(bin_file, "wb");
    if (!fb) {
        perror("Failed to create binary file");
        return 1;
    }
    fwrite(points, sizeof(TelemetryPoint), 3, fb);
    fclose(fb);

    printf("\n=== Demonstration 3: Random-Access Record Seeking ===\n");
    fb = fopen(bin_file, "rb");
    if (fb) {
        // Direct seek to record 1 (cpu_usage is 0, mem_usage is 1)
        fseek(fb, 1 * (long)sizeof(TelemetryPoint), SEEK_SET);
        TelemetryPoint p1;
        fread(&p1, sizeof(TelemetryPoint), 1, fb);
        printf("  Direct Seek Record 1 -> ID: %u, Key: %s, Value: %.2f\n",
               p1.record_id, p1.key, p1.value);

        // Check file size using ftell
        fseek(fb, 0, SEEK_END);
        long total_bytes = ftell(fb);
        printf("  Total Binary File Size: %ld bytes (Expected %zu bytes)\n",
               total_bytes, 3 * sizeof(TelemetryPoint));
        fclose(fb);
    }

    // Clean up temporary lab files
    remove(text_file);
    remove(bin_file);
    return 0;
}
