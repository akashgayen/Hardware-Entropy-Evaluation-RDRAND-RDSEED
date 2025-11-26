#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chisquare

# ------------------------------------------------------------
# Load collected data from collector.c output
# ------------------------------------------------------------
def load_data(rdrand_file="rdrand_raw.bin", rdseed_file="rdseed_raw.bin"):
    rdrand = np.fromfile(rdrand_file, dtype=np.uint64)
    rdseed = np.fromfile(rdseed_file, dtype=np.uint64)
    return rdrand, rdseed


# ------------------------------------------------------------
# Compute Shannon entropy in bits
# ------------------------------------------------------------
def shannon_entropy(values):
    byte_array = np.frombuffer(values.tobytes(), dtype=np.uint8)
    counts = np.bincount(byte_array, minlength=256)
    p = counts / counts.sum()
    p_nonzero = p[p > 0]
    return -np.sum(p_nonzero * np.log2(p_nonzero))


# ------------------------------------------------------------
# Bit frequency test (0/1 balance)
# ------------------------------------------------------------
def bit_frequency(values):
    bits = np.unpackbits(values.view(np.uint8))
    ones = bits.sum()
    zeros = len(bits) - ones
    return zeros, ones


# ------------------------------------------------------------
# Autocorrelation test for randomness
# ------------------------------------------------------------
def autocorrelation(values, lag=1):
    x = values.astype(np.float64)
    return np.corrcoef(x[:-lag], x[lag:])[0, 1]


# ------------------------------------------------------------
# Plot histogram
# ------------------------------------------------------------
def plot_hist(values, title, filename):
    plt.figure(figsize=(8,5))
    plt.hist(values, bins=100)
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# ------------------------------------------------------------
# Scatter plot RDRAND vs RDSEED
# ------------------------------------------------------------
def scatter_compare(a, b, filename):
    plt.figure(figsize=(6,6))
    plt.scatter(a[:5000], b[:5000], s=1)
    plt.title("RDRAND vs RDSEED (First 5000 Samples)")
    plt.xlabel("RDRAND")
    plt.ylabel("RDSEED")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# ------------------------------------------------------------
# Chi-Square uniform distribution test
# ------------------------------------------------------------
def chi_square_test(values):
    byte_array = np.frombuffer(values.tobytes(), dtype=np.uint8)
    counts = np.bincount(byte_array, minlength=256)
    expected = np.full(256, len(byte_array) / 256)
    chi, p = chisquare(counts, expected)
    return chi, p


# ------------------------------------------------------------
# Full analysis pipeline
# ------------------------------------------------------------
def main():
    rdrand, rdseed = load_data()

    print("\n================ RDRAND ANALYSIS ================\n")
    print("Samples:", len(rdrand))
    print("Shannon Entropy:", shannon_entropy(rdrand))
    zeros, ones = bit_frequency(rdrand)
    print("Bit Frequency -> 0s:", zeros, " 1s:", ones)
    print("Autocorrelation:", autocorrelation(rdrand))
    print("Chi-Square Test:", chi_square_test(rdrand))

    plot_hist(rdrand, "RDRAND Histogram", "rdrand_hist.png")


    print("\n================ RDSEED ANALYSIS ================\n")
    print("Samples:", len(rdseed))
    print("Shannon Entropy:", shannon_entropy(rdseed))
    zeros, ones = bit_frequency(rdseed)
    print("Bit Frequency -> 0s:", zeros, " 1s:", ones)
    print("Autocorrelation:", autocorrelation(rdseed))
    print("Chi-Square Test:", chi_square_test(rdseed))

    plot_hist(rdseed, "RDSEED Histogram", "rdseed_hist.png")


    print("\n================ COMPARISON ================\n")
    scatter_compare(rdrand, rdseed, "scatter_rdrand_rdseed.png")
    print("Scatter plot saved.")


if __name__ == "__main__":
    main()
