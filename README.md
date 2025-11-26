**Hardware Entropy Evaluation — RDRAND & RDSEED**

This project collects raw 64-bit samples from Intel's on-chip hardware RNG instructions (`RDRAND` and `RDSEED`) and provides a simple Python analysis pipeline to evaluate basic randomness properties. It is intended for experimental evaluation, teaching, and quick sanity checks — not as a certification-grade statistical test suite.

**Repository Contents**

- `collector.c`: Small C program that samples `RDRAND` and `RDSEED` into binary files.
- `analysis.py`: Python script to compute basic statistics and generate plots (histogram, scatter) from the collected data.
- `rdrand_raw.bin`, `rdseed_raw.bin`: Output files produced by `collector.c` (binary arrays of `uint64`).

**Why this project**

- **Purpose**: Compare the behavior of `RDRAND` and `RDSEED` using a reproducible capture + analysis flow.
- **Scope**: Basic metrics (Shannon entropy, bit frequency, autocorrelation, chi-square) and simple visualizations. For more advanced testing use NIST STS, Dieharder, or TestU01.

**Requirements & Hardware**

- **CPU**: x86_64 processor that supports `RDRAND` and `RDSEED` (Intel/compatible CPU with these instructions enabled).
- **Compiler**: `gcc` or compatible C compiler supporting `<immintrin.h>` builtins.
- **Python**: Python 3 with `numpy`, `matplotlib`, and `scipy` for the analysis.

**Build the collector**
Compile `collector.c` with a modern GCC. Example (recommended):

```fish
gcc -O2 -march=native -o collector collector.c
```

Notes:

- The program uses `_rdrand64_step` and `_rdseed64_step` from `<immintrin.h>`.
- `-march=native` helps the compiler generate optimal instructions for your CPU; it is optional.

**Run the collector**
Usage:

```fish
./collector <num_samples>
```

Example (collect 1,000,000 samples each):

```fish
./collector 1000000
```

Outputs produced:

- `rdrand_raw.bin`: binary file containing `num_samples` 64-bit unsigned integers from `RDRAND`.
- `rdseed_raw.bin`: binary file containing `num_samples` 64-bit unsigned integers from `RDSEED`.

Implementation notes (see `collector.c`):

- `CHUNK_SIZE` is 65536 — samples are collected in chunks to reduce I/O overhead.
- `rdrand_u64_retry` attempts 2000 iterations to obtain a `RDRAND` value before erroring.
- `rdseed_u64_retry` attempts 200000 iterations and calls `usleep(1)` periodically to let hardware refill entropy. `RDSEED` may fail if the CPU's entropy pool is temporarily empty.

**Python analysis (`analysis.py`)**

Install dependencies (recommended to use a virtual environment):

```fish
python3 -m venv env
source env/bin/activate.fish
pip install --upgrade pip
pip install numpy matplotlib scipy
```

Run the analysis (reads `rdrand_raw.bin` and `rdseed_raw.bin` in the current directory):

```fish
python3 analysis.py
```

What `analysis.py` does:

- Loads the two binary files into `numpy` arrays (`dtype=uint64`).
- Computes Shannon entropy (on the byte stream obtained from the samples).
- Computes bit frequency (counts of 0 and 1 across all bits).
- Computes a simple lag-1 autocorrelation across 64-bit sample values.
- Runs a chi-square test treating byte values as categories (256 buckets).
- Writes visual outputs: `rdrand_hist.png`, `rdseed_hist.png`, and `scatter_rdrand_rdseed.png` (first 5000 samples).

Interpreting results (guidelines):

- **Shannon Entropy**: Computed over bytes, an ideal uniformly random source should be near 8.0 bits per byte. Slight deviations are expected for finite samples.
- **Bit Frequency**: Ones vs zeros should be close to parity (50/50) across a large sample set. Small differences are normal; large systematic biases are suspicious.
- **Autocorrelation**: Values near 0 indicate little linear correlation between adjacent samples. Large magnitude indicates correlation in the output stream.
- **Chi-Square Test**: Tests uniformity of byte frequencies. A large p-value (e.g., > 0.01) indicates no evidence to reject uniformity; a very small p-value suggests non-uniform behavior. Use caution: chi-square assumptions require sufficiently large counts per bucket.

**Example workflow**

1. Build collector: `gcc -O2 -march=native -o collector collector.c`
2. Collect 10 million samples: `./collector 10000000`
3. Activate Python venv and run analysis: `python3 analysis.py`
4. Inspect `*_hist.png` and `scatter_rdrand_rdseed.png` and review printed statistics.

**Troubleshooting**

- If `RDSEED failure.` appears, the program could not retrieve a `RDSEED` value after many retries. Possible mitigations:
  - Reduce collection rate (collect fewer samples per second) or allow small sleeps between reads.
  - Run on a different kernel/platform state — heavy CPU load or virtualization may affect availability.
  - Increase retry count in `rdseed_u64_retry` (edit `collector.c`) — note this will slow collection.
- If the compiler complains about `_rdrand64_step` / `_rdseed64_step`, ensure you include `<immintrin.h>` and compile with a modern GCC/Clang.
- If `analysis.py` errors importing modules, check your Python `venv` and installed packages.

**Caveats & Limitations**

- This tool is for exploratory evaluation only and does not replace formal test suites like NIST STS or TestU01.
- Collected samples are raw hardware outputs; post-processing, whitening, or conditioning (used by OS RNGs) is not performed here.
- Results depend heavily on sample size and the machine's runtime conditions.

**Next steps & suggestions**

- Run larger sample sizes (10M+ samples) to reduce variance in statistical estimates.
- Use specialized test suites: integrate with NIST STS, Dieharder, or TestU01 for comprehensive testing.
- Compare with OS-provided entropy sources: sample `/dev/random` and `/dev/urandom` for comparison.
- Add additional metrics: entropy estimators, spectral tests, runs tests, and higher-lag autocorrelations.

**License & Contact**

- This repository is provided as-is for research and educational use. If you want a permissive license, add one (e.g., MIT) in a `LICENSE` file.
- For questions or suggestions, open an issue or contact the repository owner.

**Acknowledgements**

- This project uses simple building blocks (GCC, Python, NumPy, Matplotlib, SciPy) to create a minimal, portable evaluation pipeline.

--
