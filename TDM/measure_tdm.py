#!uv run --script
# /// script
# dependencies = [
#   "numpy",
#   "soundfile",
#   "typer",
# ]
# ///

"""
Measure THD+N of a captured audio file.
"""

from pathlib import Path
import numpy as np
import soundfile as sf
import typer


def thd_thdn(x, fs, f0_hint=1000.0, bw=(20, 20000), max_h=10, nb=5):
    # x can be (N,) or (N,C)
    x = np.asarray(x)
    if x.ndim == 2:
        rms = np.sqrt(np.mean(x**2, axis=0))
        x = x[:, int(np.argmax(rms))]
    assert np.isfinite(x).all(), "Input has NaNs/Inf"
    x = x - np.mean(x)

    # pick N (power of two, not larger than input)
    N = 1 << (len(x) - 1).bit_length()
    if N > len(x):
        N >>= 1
    x = x[:N]
    if N < 4096:
        raise ValueError("Not enough samples")

    w = np.hanning(N)
    X = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(N, 1 / fs)
    P = np.abs(X) ** 2  # consistent power units for ratios

    # bandlimit
    bw_lo, bw_hi = bw[0], (bw[1] if bw[1] is not None else fs / 2)
    inband = (freqs >= max(20, freqs[1])) & (freqs <= bw_hi)

    # find fundamental near hint (±5%)
    kband = (freqs >= 0.95 * f0_hint) & (freqs <= 1.05 * f0_hint)
    if not np.any(kband):
        kband = inband
    k0 = np.flatnonzero(kband)[np.argmax(P[kband])]

    # integrate the fundamental mainlobe (±nb bins)
    kf0_lo = max(0, k0 - nb)
    kf0_hi = min(len(P), k0 + nb + 1)
    V1p = np.sum(P[kf0_lo:kf0_hi])
    if V1p <= 1e-24:
        raise ValueError("Fundamental too small or not found.")

    # THD: sum power in harmonic mainlobes (within Nyquist & band)
    harm_p = 0.0
    f0 = freqs[k0]
    for k in range(2, max_h + 1):
        fk = k * f0
        if fk >= fs / 2 or fk > bw_hi:
            break
        hk = np.argmin(np.abs(freqs - fk))
        lo = max(0, hk - nb)
        hi = min(len(P), hk + nb + 1)
        harm_p += np.sum(P[lo:hi])

    THD = np.sqrt(harm_p) / np.sqrt(V1p)

    # THD+N: everything in band except the fundamental mainlobe
    residual = inband.copy()
    residual[kf0_lo:kf0_hi] = False
    # (optional) notch mains:
    for hz in (50, 60, 100, 120, 150, 180):
        j = np.argmin(np.abs(freqs - hz))
        residual[max(0, j - 1) : min(len(P), j + 2)] = False

    THDN = np.sqrt(np.sum(P[residual])) / np.sqrt(V1p)

    thd_db = -np.inf if THD == 0 else 20 * np.log10(THD)
    thdn_db = -np.inf if THDN == 0 else 20 * np.log10(THDN)

    fund_dbfs = 20 * np.log10(
        np.sqrt(np.sum(np.abs(X[kf0_lo:kf0_hi]) ** 2))
        / (np.sqrt(np.sum(np.abs(X) ** 2)) + 1e-20)
    )
    noise_dbfs = 20 * np.log10(
        np.sqrt(np.sum(P[residual])) / (np.sqrt(np.sum(np.abs(X) ** 2)) + 1e-20)
    )
    print(f"Fund ~{fund_dbfs:.1f} dBFS, Residual ~{noise_dbfs:.1f} dBFS")

    sinad_db = -20 * np.log10(THDN)  # same bandwidth as THD+N
    enob = (sinad_db - 1.76) / 6.02
    print(f"SINAD {sinad_db:.1f} dB, ENOB {enob:.2f} bits")

    return THD, thd_db, THDN, thdn_db


def main(file: Path):
    x, fs = sf.read(file, always_2d=True)
    x = x[:, 0]
    THD, thd_db, THDN, thdn_db = thd_thdn(x, fs, f0_hint=997.0, bw=(20, 20000))
    print(THD, thd_db, THDN, thdn_db)


if __name__ == "__main__":
    typer.run(main)
