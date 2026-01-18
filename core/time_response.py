"""Time-domain response calculations for SDOF systems."""

import numpy as np
from numpy.typing import NDArray
from scipy import signal

from .sdof_system import SDOFSystem


def compute_impulse_response(
    system: SDOFSystem,
    time: NDArray[np.floating]
) -> NDArray[np.floating]:
    """Compute impulse response h(t) of the SDOF system.

    For underdamped system (ζ < 1):
        h(t) = (1/mωd) * exp(-ζωn*t) * sin(ωd*t)

    For critically damped (ζ = 1):
        h(t) = (1/m) * t * exp(-ωn*t)

    For overdamped (ζ > 1):
        h(t) = (1/mωn√(ζ²-1)) * exp(-ζωn*t) * sinh(ωn√(ζ²-1)*t)

    Args:
        system: SDOF system parameters
        time: Time array in seconds

    Returns:
        Impulse response array (displacement per unit impulse)
    """
    m = system.mass
    wn = system.natural_frequency
    zeta = system.damping_ratio

    t = np.asarray(time)
    h = np.zeros_like(t)

    # Only compute for t >= 0
    mask = t >= 0

    if system.is_underdamped:
        wd = system.damped_frequency
        h[mask] = (1 / (m * wd)) * np.exp(-zeta * wn * t[mask]) * np.sin(wd * t[mask])

    elif system.is_critically_damped:
        h[mask] = (1 / m) * t[mask] * np.exp(-wn * t[mask])

    else:  # Overdamped
        wd_imag = wn * np.sqrt(zeta**2 - 1)
        h[mask] = (1 / (m * wd_imag)) * np.exp(-zeta * wn * t[mask]) * np.sinh(wd_imag * t[mask])

    return h


def compute_step_response(
    system: SDOFSystem,
    time: NDArray[np.floating],
    force_magnitude: float = 1.0
) -> NDArray[np.floating]:
    """Compute step response of the SDOF system.

    For underdamped system (ζ < 1):
        x(t) = (F0/k) * [1 - exp(-ζωn*t) * (cos(ωd*t) + (ζ/√(1-ζ²))*sin(ωd*t))]

    Args:
        system: SDOF system parameters
        time: Time array in seconds
        force_magnitude: Step force magnitude in N (default 1.0)

    Returns:
        Step response array (displacement)
    """
    k = system.stiffness
    wn = system.natural_frequency
    zeta = system.damping_ratio

    t = np.asarray(time)
    x = np.zeros_like(t)

    # Static deflection
    x_static = force_magnitude / k

    # Only compute for t >= 0
    mask = t >= 0

    if system.is_underdamped:
        wd = system.damped_frequency
        sqrt_term = np.sqrt(1 - zeta**2)
        x[mask] = x_static * (
            1 - np.exp(-zeta * wn * t[mask]) * (
                np.cos(wd * t[mask]) + (zeta / sqrt_term) * np.sin(wd * t[mask])
            )
        )

    elif system.is_critically_damped:
        x[mask] = x_static * (1 - (1 + wn * t[mask]) * np.exp(-wn * t[mask]))

    else:  # Overdamped
        s1 = -wn * (zeta - np.sqrt(zeta**2 - 1))
        s2 = -wn * (zeta + np.sqrt(zeta**2 - 1))
        x[mask] = x_static * (
            1 + (s1 * np.exp(s2 * t[mask]) - s2 * np.exp(s1 * t[mask])) / (s2 - s1)
        )

    return x


def compute_harmonic_response(
    system: SDOFSystem,
    time: NDArray[np.floating],
    excitation_frequency: float,
    force_amplitude: float = 1.0,
    include_transient: bool = True
) -> NDArray[np.floating]:
    """Compute response to harmonic excitation F(t) = F0*sin(ωt).

    Steady-state response:
        x(t) = X*sin(ωt - φ)

    where X = F0 / √[(k-mω²)² + (cω)²]
    and φ = arctan(cω / (k-mω²))

    Args:
        system: SDOF system parameters
        time: Time array in seconds
        excitation_frequency: Excitation frequency in Hz
        force_amplitude: Force amplitude in N (default 1.0)
        include_transient: Include transient response (default True)

    Returns:
        Displacement response array
    """
    m = system.mass
    k = system.stiffness
    c = system.damping
    wn = system.natural_frequency
    zeta = system.damping_ratio

    omega = 2 * np.pi * excitation_frequency
    t = np.asarray(time)

    # Steady-state amplitude and phase
    denom = np.sqrt((k - m * omega**2)**2 + (c * omega)**2)
    X = force_amplitude / denom
    phi = np.arctan2(c * omega, k - m * omega**2)

    # Steady-state response
    x_steady = X * np.sin(omega * t - phi)

    if not include_transient:
        return x_steady

    # Add transient response for zero initial conditions
    # Transient dies out as exp(-ζωn*t)
    mask = t >= 0
    x_transient = np.zeros_like(t)

    if system.is_underdamped:
        wd = system.damped_frequency
        # Initial conditions to cancel steady-state at t=0
        x0 = -X * np.sin(-phi)  # x(0) = 0
        v0 = -X * omega * np.cos(-phi)  # v(0) = 0

        A = x0
        B = (v0 + zeta * wn * x0) / wd

        x_transient[mask] = np.exp(-zeta * wn * t[mask]) * (
            A * np.cos(wd * t[mask]) + B * np.sin(wd * t[mask])
        )

    return x_steady + x_transient


def compute_free_vibration(
    system: SDOFSystem,
    time: NDArray[np.floating],
    initial_displacement: float = 1.0,
    initial_velocity: float = 0.0
) -> NDArray[np.floating]:
    """Compute free vibration response with initial conditions.

    Args:
        system: SDOF system parameters
        time: Time array in seconds
        initial_displacement: Initial displacement x(0) in m
        initial_velocity: Initial velocity v(0) in m/s

    Returns:
        Free vibration response array
    """
    wn = system.natural_frequency
    zeta = system.damping_ratio
    x0 = initial_displacement
    v0 = initial_velocity

    t = np.asarray(time)
    x = np.zeros_like(t)
    mask = t >= 0

    if system.is_underdamped:
        wd = system.damped_frequency
        A = x0
        B = (v0 + zeta * wn * x0) / wd

        x[mask] = np.exp(-zeta * wn * t[mask]) * (
            A * np.cos(wd * t[mask]) + B * np.sin(wd * t[mask])
        )

    elif system.is_critically_damped:
        A = x0
        B = v0 + wn * x0
        x[mask] = (A + B * t[mask]) * np.exp(-wn * t[mask])

    else:  # Overdamped
        sqrt_term = np.sqrt(zeta**2 - 1)
        s1 = wn * (-zeta + sqrt_term)
        s2 = wn * (-zeta - sqrt_term)

        A = (v0 - s2 * x0) / (s1 - s2)
        B = (s1 * x0 - v0) / (s1 - s2)

        x[mask] = A * np.exp(s1 * t[mask]) + B * np.exp(s2 * t[mask])

    return x


def decay_envelope(
    system: SDOFSystem,
    time: NDArray[np.floating],
    initial_amplitude: float = 1.0
) -> NDArray[np.floating]:
    """Compute the exponential decay envelope for underdamped response.

    Envelope: A(t) = A0 * exp(-ζωn*t)

    Args:
        system: SDOF system parameters
        time: Time array in seconds
        initial_amplitude: Initial amplitude

    Returns:
        Decay envelope array
    """
    t = np.asarray(time)
    mask = t >= 0
    envelope = np.zeros_like(t)

    zeta = system.damping_ratio
    wn = system.natural_frequency

    envelope[mask] = initial_amplitude * np.exp(-zeta * wn * t[mask])

    return envelope


def logarithmic_decrement(system: SDOFSystem) -> float:
    """Calculate the logarithmic decrement δ.

    δ = ln(x_n / x_{n+1}) = 2πζ / √(1-ζ²)

    For small damping: δ ≈ 2πζ

    Args:
        system: SDOF system

    Returns:
        Logarithmic decrement
    """
    zeta = system.damping_ratio
    if zeta >= 1.0:
        return float('inf')
    return 2 * np.pi * zeta / np.sqrt(1 - zeta**2)
