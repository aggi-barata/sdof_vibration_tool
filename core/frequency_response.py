"""Frequency Response Function (FRF) calculations for SDOF systems."""

import numpy as np
from numpy.typing import NDArray

from .sdof_system import SDOFSystem


def compute_frf(
    system: SDOFSystem,
    frequencies: NDArray[np.floating],
    output_type: str = "displacement"
) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.complexfloating]]:
    """Compute frequency response function H(ω).

    The FRF relates the output displacement to input force:
    H(ω) = X/F = 1 / ((k - mω²) + jcω)

    Args:
        system: SDOF system parameters
        frequencies: Frequency array in Hz
        output_type: Type of output ("displacement", "velocity", "acceleration")

    Returns:
        Tuple of (magnitude in dB, phase in degrees, complex FRF)
    """
    omega = 2 * np.pi * frequencies  # Convert to rad/s

    m = system.mass
    k = system.stiffness
    c = system.damping

    # Complex FRF: H(ω) = 1 / ((k - mω²) + jcω)
    denominator = (k - m * omega**2) + 1j * c * omega
    H = 1.0 / denominator

    # Modify for output type
    if output_type == "velocity":
        H = 1j * omega * H
    elif output_type == "acceleration":
        H = -omega**2 * H

    # Magnitude in dB (reference: static compliance 1/k)
    magnitude_db = 20 * np.log10(np.abs(H) * k)

    # Phase in degrees
    phase_deg = np.degrees(np.angle(H))

    return magnitude_db, phase_deg, H


def compute_frf_normalized(
    zeta: float,
    frequency_ratios: NDArray[np.floating]
) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
    """Compute normalized FRF magnitude and phase.

    Uses the normalized form: H(r) = 1 / ((1 - r²) + j2ζr)
    where r = ω/ωn is the frequency ratio.

    Args:
        zeta: Damping ratio
        frequency_ratios: Array of frequency ratios r = ω/ωn

    Returns:
        Tuple of (magnitude ratio |H|, phase in degrees)
    """
    r = frequency_ratios
    denominator = (1 - r**2) + 1j * 2 * zeta * r
    H = 1.0 / denominator

    magnitude = np.abs(H)
    phase_deg = np.degrees(np.angle(H))

    return magnitude, phase_deg


def resonance_amplitude(zeta: float) -> float:
    """Calculate the amplitude magnification at resonance.

    For underdamped systems (ζ < 1), the peak occurs near ω = ωn√(1-2ζ²)
    and the maximum amplitude is Q = 1/(2ζ√(1-ζ²)).

    For small damping, Q ≈ 1/(2ζ).

    Args:
        zeta: Damping ratio

    Returns:
        Peak amplitude magnification factor
    """
    if zeta >= 1 / np.sqrt(2):
        # No resonance peak for ζ >= 1/√2
        return 1.0

    return 1.0 / (2 * zeta * np.sqrt(1 - zeta**2))


def half_power_bandwidth(system: SDOFSystem) -> float:
    """Calculate the half-power bandwidth.

    The half-power points occur where the amplitude is 1/√2 times the peak.
    Bandwidth Δω ≈ 2ζωn for small damping.

    Args:
        system: SDOF system

    Returns:
        Half-power bandwidth in rad/s
    """
    return 2 * system.damping_ratio * system.natural_frequency
