"""Shock Response Spectrum (SRS) calculations for SDOF systems."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy import signal


def generate_shock_pulse(
    pulse_type: str,
    duration: float,
    amplitude: float,
    dt: float
) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
    """Generate a shock pulse.

    Args:
        pulse_type: Type of pulse ("half_sine", "triangular", "rectangular", "versed_sine", "trapezoidal")
        duration: Pulse duration in seconds
        amplitude: Peak amplitude (typically in g's or m/s²)
        dt: Time step in seconds

    Returns:
        Tuple of (time array, acceleration array)
    """
    # Extend time beyond pulse for residual response
    total_time = duration * 10
    t = np.arange(0, total_time, dt)
    accel = np.zeros_like(t)

    pulse_samples = int(duration / dt)
    t_pulse = t[:pulse_samples]

    if pulse_type == "half_sine":
        accel[:pulse_samples] = amplitude * np.sin(np.pi * t_pulse / duration)

    elif pulse_type == "triangular":
        mid = pulse_samples // 2
        accel[:mid] = amplitude * 2 * t_pulse[:mid] / duration
        accel[mid:pulse_samples] = amplitude * (2 - 2 * t_pulse[mid:pulse_samples] / duration)

    elif pulse_type == "rectangular":
        accel[:pulse_samples] = amplitude

    elif pulse_type == "versed_sine":
        # Versed sine (haversine): (1 - cos(2πt/T)) / 2
        accel[:pulse_samples] = amplitude * (1 - np.cos(2 * np.pi * t_pulse / duration)) / 2

    elif pulse_type == "trapezoidal":
        rise_samples = pulse_samples // 4
        hold_samples = pulse_samples // 2
        fall_start = rise_samples + hold_samples

        accel[:rise_samples] = amplitude * t_pulse[:rise_samples] / (rise_samples * dt)
        accel[rise_samples:fall_start] = amplitude
        accel[fall_start:pulse_samples] = amplitude * (1 - (t_pulse[fall_start:pulse_samples] - fall_start * dt) / (rise_samples * dt))

    elif pulse_type == "initial_peak_sawtooth":
        accel[:pulse_samples] = amplitude * (1 - t_pulse / duration)

    elif pulse_type == "terminal_peak_sawtooth":
        accel[:pulse_samples] = amplitude * t_pulse / duration

    return t, accel


def compute_sdof_response(
    natural_freq: float,
    damping_ratio: float,
    base_accel: NDArray[np.floating],
    dt: float
) -> NDArray[np.floating]:
    """Compute SDOF system response to base acceleration.

    Uses the Newmark-beta method for numerical integration.

    Args:
        natural_freq: Natural frequency in Hz
        damping_ratio: Damping ratio (zeta)
        base_accel: Base acceleration array
        dt: Time step

    Returns:
        Relative displacement response array
    """
    omega_n = 2 * np.pi * natural_freq
    omega_d = omega_n * np.sqrt(1 - damping_ratio**2) if damping_ratio < 1 else 0

    n = len(base_accel)
    x = np.zeros(n)  # Relative displacement
    v = np.zeros(n)  # Relative velocity
    a = np.zeros(n)  # Relative acceleration

    # Initial acceleration
    a[0] = -base_accel[0]

    # Newmark-beta parameters (average acceleration method)
    gamma = 0.5
    beta = 0.25

    # Effective stiffness
    k_eff = omega_n**2 + gamma / (beta * dt) * 2 * damping_ratio * omega_n + 1 / (beta * dt**2)

    for i in range(n - 1):
        # Effective load
        p_eff = (-base_accel[i + 1] +
                 (1 / (beta * dt**2)) * x[i] +
                 (1 / (beta * dt)) * v[i] +
                 (1 / (2 * beta) - 1) * a[i] +
                 2 * damping_ratio * omega_n * (
                     (gamma / (beta * dt)) * x[i] +
                     (gamma / beta - 1) * v[i] +
                     dt * (gamma / (2 * beta) - 1) * a[i]
                 ))

        # Solve for displacement
        x[i + 1] = p_eff / k_eff

        # Update velocity and acceleration
        v[i + 1] = (gamma / (beta * dt)) * (x[i + 1] - x[i]) + (1 - gamma / beta) * v[i] + dt * (1 - gamma / (2 * beta)) * a[i]
        a[i + 1] = (1 / (beta * dt**2)) * (x[i + 1] - x[i]) - (1 / (beta * dt)) * v[i] - (1 / (2 * beta) - 1) * a[i]

    return x


def compute_srs(
    base_accel: NDArray[np.floating],
    dt: float,
    frequencies: NDArray[np.floating],
    damping_ratio: float = 0.05,
    srs_type: str = "maxi-max"
) -> dict[str, NDArray[np.floating]]:
    """Compute Shock Response Spectrum.

    Args:
        base_accel: Base acceleration time history
        dt: Time step in seconds
        frequencies: Array of natural frequencies to evaluate (Hz)
        damping_ratio: Damping ratio for all oscillators (default 5%)
        srs_type: Type of SRS ("maxi-max", "primary", "residual", "all")

    Returns:
        Dictionary with SRS results:
        - "frequencies": Frequency array
        - "maxi_max": Maximum of absolute response (primary + residual)
        - "primary_pos": Maximum positive during shock
        - "primary_neg": Maximum negative during shock
        - "residual_pos": Maximum positive after shock
        - "residual_neg": Maximum negative after shock
    """
    n_freq = len(frequencies)

    # Find approximate end of shock (where input drops below 1% of peak)
    peak_accel = np.max(np.abs(base_accel))
    shock_end_idx = len(base_accel) - 1
    for i in range(len(base_accel) - 1, -1, -1):
        if np.abs(base_accel[i]) > 0.01 * peak_accel:
            shock_end_idx = i
            break

    # Initialize result arrays
    maxi_max = np.zeros(n_freq)
    primary_pos = np.zeros(n_freq)
    primary_neg = np.zeros(n_freq)
    residual_pos = np.zeros(n_freq)
    residual_neg = np.zeros(n_freq)

    for i, fn in enumerate(frequencies):
        # Compute response
        x = compute_sdof_response(fn, damping_ratio, base_accel, dt)

        # Convert to pseudo-acceleration (omega_n^2 * x)
        omega_n = 2 * np.pi * fn
        response = omega_n**2 * x

        # Primary (during shock)
        primary_response = response[:shock_end_idx + 1]
        primary_pos[i] = np.max(primary_response)
        primary_neg[i] = np.min(primary_response)

        # Residual (after shock)
        residual_response = response[shock_end_idx + 1:]
        if len(residual_response) > 0:
            residual_pos[i] = np.max(residual_response)
            residual_neg[i] = np.min(residual_response)

        # Maxi-max (maximum absolute value overall)
        maxi_max[i] = np.max(np.abs(response))

    return {
        "frequencies": frequencies,
        "maxi_max": maxi_max,
        "primary_pos": primary_pos,
        "primary_neg": np.abs(primary_neg),
        "residual_pos": residual_pos,
        "residual_neg": np.abs(residual_neg),
    }


def compute_srs_from_pulse(
    pulse_type: str,
    pulse_duration: float,
    pulse_amplitude: float,
    frequencies: NDArray[np.floating],
    damping_ratio: float = 0.05,
    srs_type: str = "maxi-max"
) -> dict[str, NDArray[np.floating]]:
    """Compute SRS for a standard shock pulse.

    Args:
        pulse_type: Type of pulse
        pulse_duration: Pulse duration in seconds
        pulse_amplitude: Peak amplitude
        frequencies: Array of natural frequencies (Hz)
        damping_ratio: Damping ratio
        srs_type: Type of SRS

    Returns:
        SRS results dictionary
    """
    # Determine appropriate time step (at least 10 points per highest frequency cycle)
    max_freq = np.max(frequencies)
    dt = 1 / (max_freq * 20)

    # Generate pulse
    t, accel = generate_shock_pulse(pulse_type, pulse_duration, pulse_amplitude, dt)

    # Compute SRS
    return compute_srs(accel, dt, frequencies, damping_ratio, srs_type)
