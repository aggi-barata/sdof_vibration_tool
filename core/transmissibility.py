"""Transmissibility calculations for SDOF systems."""

import numpy as np
from typing import Tuple, List
from .sdof_system import SDOFSystem


def compute_transmissibility(
    system: SDOFSystem,
    frequencies: np.ndarray,
    freq_unit: str = "rad/s"
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute force/displacement transmissibility for an SDOF system.
    
    TR = |Ft/F| = |X_base/X| = sqrt[(1 + (2ζr)²) / ((1-r²)² + (2ζr)²)]
    where r = ω/ωn
    
    Args:
        system: SDOFSystem instance
        frequencies: Array of frequencies
        freq_unit: "rad/s" or "hz"
    
    Returns:
        Tuple of (frequency ratios r, transmissibility TR)
    """
    if freq_unit.lower() == "hz":
        omega = 2 * np.pi * frequencies
    else:
        omega = frequencies
    
    omega_n = system.natural_frequency
    zeta = system.damping_ratio
    
    r = omega / omega_n
    
    TR = compute_transmissibility_normalized(zeta, r)
    
    return r, TR


def compute_transmissibility_normalized(
    zeta: float,
    frequency_ratios: np.ndarray
) -> np.ndarray:
    """Compute normalized transmissibility.
    
    TR = sqrt[(1 + (2ζr)²) / ((1-r²)² + (2ζr)²)]
    
    Args:
        zeta: Damping ratio
        frequency_ratios: Array of r = ω/ωn values
    
    Returns:
        Array of transmissibility values
    """
    r = frequency_ratios
    
    numerator = 1 + (2 * zeta * r)**2
    denominator = (1 - r**2)**2 + (2 * zeta * r)**2
    
    TR = np.sqrt(numerator / denominator)
    
    return TR


def compute_transmissibility_multi_zeta(
    zeta_values: List[float],
    frequency_ratios: np.ndarray
) -> List[np.ndarray]:
    """Compute transmissibility for multiple damping ratios.
    
    Args:
        zeta_values: List of damping ratios
        frequency_ratios: Array of r = ω/ωn values
    
    Returns:
        List of transmissibility arrays, one per zeta value
    """
    return [compute_transmissibility_normalized(zeta, frequency_ratios) 
            for zeta in zeta_values]


def find_crossover_frequency() -> float:
    """Find the frequency ratio where all TR curves cross.
    
    All transmissibility curves cross at r = sqrt(2), where TR = 1
    for any damping ratio.
    
    Returns:
        Crossover frequency ratio (sqrt(2) ≈ 1.414)
    """
    return np.sqrt(2)


def find_resonance_frequency(zeta: float) -> float:
    """Find the frequency ratio at peak transmissibility.
    
    For an underdamped system (ζ < 1/√2), peak occurs at:
    r_peak = sqrt(sqrt(1 + 8ζ²) - 1) / (2ζ) for ζ < 0.5
    
    For heavily damped systems, peak is at r = 0.
    
    Args:
        zeta: Damping ratio
    
    Returns:
        Frequency ratio at resonance
    """
    if zeta >= 1 / np.sqrt(2):
        return 0.0
    
    # For TR, the peak is slightly different from FRF
    # Peak occurs where d(TR)/dr = 0
    # For small damping, it's approximately at r ≈ 1
    return np.sqrt(1 - 2 * zeta**2) if zeta < 0.5 else 0.0


def peak_transmissibility(zeta: float) -> float:
    """Calculate the peak transmissibility value.
    
    Q = 1 / (2ζ) for small damping (ζ << 1)
    
    Args:
        zeta: Damping ratio
    
    Returns:
        Peak transmissibility value
    """
    if zeta <= 0:
        return np.inf
    if zeta >= 1 / np.sqrt(2):
        return 1.0
    
    r_peak = find_resonance_frequency(zeta)
    if r_peak == 0:
        return 1.0
    
    return compute_transmissibility_normalized(zeta, np.array([r_peak]))[0]
