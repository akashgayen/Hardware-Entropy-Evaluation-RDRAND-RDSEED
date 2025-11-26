#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <immintrin.h>
#include <unistd.h>

#define CHUNK_SIZE 65536

#define FILE_RDRAND "rdrand_raw.bin"
#define FILE_RDSEED "rdseed_raw.bin"

static inline int rdrand_u64_retry(unsigned long long *value) {
    for (int i = 0; i < 2000; i++) {
        if (_rdrand64_step(value))
            return 1;
    }
    return 0;
}

static inline int rdseed_u64_retry(unsigned long long *value) {
    for (int i = 0; i < 200000; i++) {        // 200k retries
        if (_rdseed64_step(value))
            return 1;

        // Give hardware time to refill entropy pool
        if (i % 50 == 0)
            usleep(1);   // sleep 1 microsecond
    }
    return 0; // true failure
}

int main(int argc, char *argv[]) {

    if (argc != 2) {
        printf("Usage: %s <num_samples>\n", argv[0]);
        return 1;
    }

    long long total = atoll(argv[1]);
    long long collected = 0;

    FILE *fp_rdrand = fopen(FILE_RDRAND, "wb");
    FILE *fp_rdseed = fopen(FILE_RDSEED, "wb");

    if (!fp_rdrand || !fp_rdseed) {
        printf("Error: cannot open output files.\n");
        return 1;
    }

    unsigned long long *buf_rdrand =
        malloc(CHUNK_SIZE * sizeof(unsigned long long));
    unsigned long long *buf_rdseed =
        malloc(CHUNK_SIZE * sizeof(unsigned long long));

    if (!buf_rdrand || !buf_rdseed) {
        printf("Memory allocation failed.\n");
        return 1;
    }

    printf("Collecting %lld samples each from RDRAND and RDSEED...\n", total);

    while (collected < total) {
        long long to_read =
            (total - collected > CHUNK_SIZE ? CHUNK_SIZE : total - collected);

        for (long long i = 0; i < to_read; i++) {

            if (!rdrand_u64_retry(&buf_rdrand[i])) {
                printf("RDRAND failure.\n");
                return 1;
            }

            if (!rdseed_u64_retry(&buf_rdseed[i])) {
                printf("RDSEED failure.\n");
                return 1;
            }
        }

        fwrite(buf_rdrand, sizeof(unsigned long long), to_read, fp_rdrand);
        fwrite(buf_rdseed, sizeof(unsigned long long), to_read, fp_rdseed);

        collected += to_read;

        if (collected % (CHUNK_SIZE * 20) == 0)
            printf("Progress: %lld / %lld\n", collected, total);
    }

    printf("Done.\nSaved:\n  %s\n  %s\n", FILE_RDRAND, FILE_RDSEED);

    free(buf_rdrand);
    free(buf_rdseed);
    fclose(fp_rdrand);
    fclose(fp_rdseed);

    return 0;
}
