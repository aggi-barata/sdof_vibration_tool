"""Frequency Response Function (FRF) calculations for SDOF systems."""

import numpy as np
from typing import Tuple
from .sdof_system import SDOFSystem


def compute_frf(
    system: SDOFSystem,
    frequencies: np.ndarray,
    freq_unit: str = "rad/s"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute the frequency response function H(ω) for an SDOF system.
    
    The FRF is defined as: H(ω) = X/F = 1/((k - mω²) + jcω)
    
    Args:
        system: SDOFSystem instance
        frequencies: Array of frequencies
        freq_unit: "rad/s" or "hz"
    
    Returns:
        Tuple of (frequencies in rad/s, magnitude, phase in degrees)
    """
    if freq_unit.lower() == "hz":
        omega = 2 * np.pi * frequencies
    else:
        omega = frequencies
    
    m = system.mass
    k = system.stiffness
    c = system.damping
    
    # Complex FRF: H(ω) = 1 / ((k - mω²) + jcω)
    denominator = (k - m * omega**2) + 1j * c * omega
    H = 1.0 / denominator
    
    magnitude = np.abs(H)
    phase = np.angle(H, deg=True)
    
    return omega, magnitude, phase


def compute_frf_normalized(
    zeta: float,
    frequency_ratios: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute normalized FRF magnitude and phase.
    
    Normalized form: H(r) = 1 / ((1 - r²) + j(2ζr))
    where r = ω/ωn is the frequency ratio.
    
    Args:
        zeta: Damping ratio
        frequency_ratios: Array of r = ω/ωn values
    
    Returns:
        Tuple of (magnitude normalized by 1/k, phase in degrees)
    """
    r = frequency_ratios
    
    denominator = (1 - r**2) + 1j * (2 * zeta * r)
    H_norm = 1.0 / denominator
    
    magnitude = np.abs(H_norm)
    phase = np.angle(H_norm, deg=True)
    
    return magnitude, phase


def magnitude_to_db(magnitude: np.ndarray) -> np.ndarray:
    """Convert magnitude to decibels (dB)."""
    return 20 * np.log10(magnitude)


def generate_frequency_array(
    f_min: float,
    f_max: float,
    n_points: int = 1000,
    log_scale: bool = True
) -> np.ndarray:
    """Generate an array of frequencies for FRF calculation.
    
    Args:
        f_min: Minimum frequency
        f_max: Maximum frequency
        n_points: Number of frequency points
        log_scale: Use logarithmic spacing if True
    
    Returns:
        Array of frequencies
    """
    if log_scale:
        return np.logspace(np.log10(f_min), np.log10(f_max), n_points)
    else:
        return np.linspace(f_min, f_max, n_points)
