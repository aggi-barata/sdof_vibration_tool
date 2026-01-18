"""Transmissibility calculations for SDOF systems."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .sdof_system import SDOFSystem


def compute_transmissibility(
    system: SDOFSystem,
    frequencies: NDArray[np.floating]
) -> NDArray[np.floating]:
    """Compute force or displacement transmissibility TR(ω).

    TR = |Ft/F0| = |X/Y| = √[(1 + (2ζr)²) / ((1-r²)² + (2ζr)²)]

    where r = ω/ωn is the frequency ratio.

    Args:
        system: SDOF system parameters
        frequencies: Frequency array in Hz

    Returns:
        Transmissibility array (dimensionless)
    """
    omega = 2 * np.pi * frequencies
    r = omega / system.natural_frequency
    zeta = system.damping_ratio

    return compute_transmissibility_normalized(zeta, r)


def compute_transmissibility_normalized(
    zeta: float | NDArray[np.floating],
    frequency_ratios: NDArray[np.floating]
) -> NDArray[np.floating]:
    """Compute normalized transmissibility.

    TR = √[(1 + (2ζr)²) / ((1-r²)² + (2ζr)²)]

    Args:
        zeta: Damping ratio (scalar or array for multiple curves)
        frequency_ratios: Array of frequency ratios r = ω/ωn

    Returns:
        Transmissibility array
    """
    r = frequency_ratios
    zeta = np.atleast_1d(zeta)

    # Handle broadcasting for multiple zeta values
    if zeta.ndim == 1 and r.ndim == 1:
        r = r[np.newaxis, :]  # Shape: (1, N)
        zeta = zeta[:, np.newaxis]  # Shape: (M, 1)

    numerator = 1 + (2 * zeta * r)**2
    denominator = (1 - r**2)**2 + (2 * zeta * r)**2

    TR = np.sqrt(numerator / denominator)

    return np.squeeze(TR)


def compute_transmissibility_db(
    system: SDOFSystem,
    frequencies: NDArray[np.floating]
) -> NDArray[np.floating]:
    """Compute transmissibility in decibels.

    Args:
        system: SDOF system parameters
        frequencies: Frequency array in Hz

    Returns:
        Transmissibility in dB (20*log10(TR))
    """
    TR = compute_transmissibility(system, frequencies)
    return 20 * np.log10(TR)


def isolation_efficiency(TR: float | NDArray[np.floating]) -> float | NDArray[np.floating]:
    """Calculate isolation efficiency from transmissibility.

    Isolation efficiency = (1 - TR) * 100%

    Positive values indicate force/motion reduction.
    Negative values indicate amplification.

    Args:
        TR: Transmissibility value(s)

    Returns:
        Isolation efficiency in percent
    """
    return (1 - TR) * 100


def crossover_frequency_ratio() -> float:
    """Return the frequency ratio where TR = 1 for all damping ratios.

    At r = √2, the transmissibility equals 1 regardless of damping.
    Above this frequency, isolation begins.

    Returns:
        Crossover frequency ratio (√2 ≈ 1.414)
    """
    return np.sqrt(2)


def find_isolation_start(system: SDOFSystem) -> float:
    """Find the frequency where isolation begins (TR < 1).

    This occurs at r = √2, so f = √2 * fn.

    Args:
        system: SDOF system

    Returns:
        Isolation start frequency in Hz
    """
    return np.sqrt(2) * system.natural_frequency_hz
