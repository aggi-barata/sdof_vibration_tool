"""Time-domain response calculations for SDOF systems."""

import numpy as np
from typing import Tuple
from scipy import signal
from .sdof_system import SDOFSystem


def compute_impulse_response(
    system: SDOFSystem,
    t_end: float = None,
    n_points: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute impulse response of SDOF system.
    
    For underdamped system (ζ < 1):
    h(t) = (1/m·ωd) · exp(-ζωn·t) · sin(ωd·t)
    
    Args:
        system: SDOFSystem instance
        t_end: End time (defaults to 5 periods or 5 time constants)
        n_points: Number of time points
    
    Returns:
        Tuple of (time array, displacement response)
    """
    omega_n = system.natural_frequency
    zeta = system.damping_ratio
    m = system.mass
    
    # Default end time: 5 periods or 5 time constants
    if t_end is None:
        if zeta < 1:
            period = 2 * np.pi / system.damped_frequency
            t_end = 5 * period
        else:
            # Time constant for overdamped
            t_end = 5 / (zeta * omega_n)
    
    t = np.linspace(0, t_end, n_points)
    
    if zeta < 1:  # Underdamped
        omega_d = system.damped_frequency
        x = (1 / (m * omega_d)) * np.exp(-zeta * omega_n * t) * np.sin(omega_d * t)
    elif zeta == 1:  # Critically damped
        x = (1 / m) * t * np.exp(-omega_n * t)
    else:  # Overdamped
        s1 = -omega_n * (zeta + np.sqrt(zeta**2 - 1))
        s2 = -omega_n * (zeta - np.sqrt(zeta**2 - 1))
        A = 1 / (m * (s2 - s1))
        x = A * (np.exp(s2 * t) - np.exp(s1 * t))
    
    return t, x


def compute_step_response(
    system: SDOFSystem,
    step_magnitude: float = 1.0,
    t_end: float = None,
    n_points: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute step response of SDOF system.
    
    For underdamped system (ζ < 1):
    x(t) = (F/k) · [1 - exp(-ζωn·t) · (cos(ωd·t) + (ζωn/ωd)·sin(ωd·t))]
    
    Args:
        system: SDOFSystem instance
        step_magnitude: Magnitude of step force
        t_end: End time
        n_points: Number of time points
    
    Returns:
        Tuple of (time array, displacement response)
    """
    omega_n = system.natural_frequency
    zeta = system.damping_ratio
    k = system.stiffness
    
    # Static deflection
    x_static = step_magnitude / k
    
    # Default end time
    if t_end is None:
        if zeta < 1:
            period = 2 * np.pi / system.damped_frequency
            t_end = 5 * period
        else:
            t_end = 5 / (zeta * omega_n)
    
    t = np.linspace(0, t_end, n_points)
    
    if zeta < 1:  # Underdamped
        omega_d = system.damped_frequency
        envelope_decay = np.exp(-zeta * omega_n * t)
        oscillation = np.cos(omega_d * t) + (zeta * omega_n / omega_d) * np.sin(omega_d * t)
        x = x_static * (1 - envelope_decay * oscillation)
    elif zeta == 1:  # Critically damped
        x = x_static * (1 - (1 + omega_n * t) * np.exp(-omega_n * t))
    else:  # Overdamped
        sqrt_term = np.sqrt(zeta**2 - 1)
        s1 = -omega_n * (zeta + sqrt_term)
        s2 = -omega_n * (zeta - sqrt_term)
        A = s2 / (s2 - s1)
        B = s1 / (s1 - s2)
        x = x_static * (1 + A * np.exp(s1 * t) + B * np.exp(s2 * t))
    
    return t, x


def compute_harmonic_response(
    system: SDOFSystem,
    excitation_freq: float,
    force_amplitude: float = 1.0,
    t_end: float = None,
    n_points: int = 1000,
    freq_unit: str = "rad/s",
    include_transient: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute response to harmonic excitation F(t) = F0·sin(ω·t).
    
    Args:
        system: SDOFSystem instance
        excitation_freq: Excitation frequency
        force_amplitude: Amplitude of excitation force
        t_end: End time
        n_points: Number of time points
        freq_unit: "rad/s" or "hz"
        include_transient: Include transient response (starts from rest)
    
    Returns:
        Tuple of (time, total response, steady-state response)
    """
    if freq_unit.lower() == "hz":
        omega = 2 * np.pi * excitation_freq
    else:
        omega = excitation_freq
    
    m = system.mass
    k = system.stiffness
    c = system.damping
    omega_n = system.natural_frequency
    zeta = system.damping_ratio
    
    # Default end time: 10 periods of excitation or natural frequency
    if t_end is None:
        period = 2 * np.pi / max(omega, omega_n)
        t_end = 10 * period
    
    t = np.linspace(0, t_end, n_points)
    
    # Steady-state response amplitude and phase
    r = omega / omega_n
    X0 = force_amplitude / k  # Static deflection
    
    denominator = np.sqrt((1 - r**2)**2 + (2 * zeta * r)**2)
    X = X0 / denominator  # Steady-state amplitude
    
    phi = np.arctan2(2 * zeta * r, 1 - r**2)  # Phase lag
    
    # Steady-state response
    x_steady = X * np.sin(omega * t - phi)
    
    if include_transient and zeta < 1:
        # Transient response (to satisfy zero initial conditions)
        omega_d = system.damped_frequency
        
        # Initial conditions for total response = 0
        x0 = 0  # Initial displacement
        v0 = 0  # Initial velocity
        
        # At t=0: x_steady(0) = -X·sin(phi)
        # At t=0: v_steady(0) = X·ω·cos(phi)
        
        # Transient must cancel steady-state at t=0
        A = -(-X * np.sin(-phi))  # = X·sin(phi)
        # v_transient(0) = -zeta·omega_n·A + omega_d·B = -X·omega·cos(phi)
        B = (-X * omega * np.cos(-phi) + zeta * omega_n * A) / omega_d
        
        x_transient = np.exp(-zeta * omega_n * t) * (A * np.cos(omega_d * t) + B * np.sin(omega_d * t))
        x_total = x_steady + x_transient
    else:
        x_total = x_steady
    
    return t, x_total, x_steady


def compute_envelope(
    system: SDOFSystem,
    t: np.ndarray,
    x0: float = 1.0
) -> np.ndarray:
    """Compute the exponential decay envelope for free vibration.
    
    Envelope: ±x0·exp(-ζωn·t)
    
    Args:
        system: SDOFSystem instance
        t: Time array
        x0: Initial amplitude
    
    Returns:
        Envelope values (positive)
    """
    return x0 * np.exp(-system.damping_ratio * system.natural_frequency * t)


def compute_free_vibration(
    system: SDOFSystem,
    time: np.ndarray,
    initial_displacement: float = 1.0,
    initial_velocity: float = 0.0
) -> np.ndarray:
    """Compute free vibration response with given initial conditions.

    Args:
        system: SDOFSystem instance
        time: Time array
        initial_displacement: Initial displacement x(0)
        initial_velocity: Initial velocity x'(0)

    Returns:
        Displacement array
    """
    omega_n = system.natural_frequency
    zeta = system.damping_ratio
    x0 = initial_displacement
    v0 = initial_velocity

    if zeta < 1:  # Underdamped
        omega_d = system.damped_frequency
        A = x0
        B = (v0 + zeta * omega_n * x0) / omega_d
        x = np.exp(-zeta * omega_n * time) * (A * np.cos(omega_d * time) + B * np.sin(omega_d * time))
    elif np.isclose(zeta, 1.0):  # Critically damped
        A = x0
        B = v0 + omega_n * x0
        x = (A + B * time) * np.exp(-omega_n * time)
    else:  # Overdamped
        sqrt_term = np.sqrt(zeta**2 - 1)
        s1 = -omega_n * (zeta + sqrt_term)
        s2 = -omega_n * (zeta - sqrt_term)
        A = (x0 * s2 - v0) / (s2 - s1)
        B = (v0 - x0 * s1) / (s2 - s1)
        x = A * np.exp(s1 * time) + B * np.exp(s2 * time)

    return x


def decay_envelope(
    system: SDOFSystem,
    time: np.ndarray,
    initial_amplitude: float = 1.0
) -> np.ndarray:
    """Compute the exponential decay envelope for free vibration.

    Envelope: A0 * exp(-ζωn·t)

    Args:
        system: SDOFSystem instance
        time: Time array
        initial_amplitude: Initial amplitude

    Returns:
        Envelope values (positive)
    """
    return initial_amplitude * np.exp(-system.damping_ratio * system.natural_frequency * time)


def get_state_space(system: SDOFSystem) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Get state-space representation of SDOF system.
    
    State vector: [x, x_dot]
    Input: Force F
    Output: Displacement x
    
    Returns:
        Tuple of (A, B, C, D) matrices
    """
    m = system.mass
    k = system.stiffness
    c = system.damping
    
    A = np.array([[0, 1],
                  [-k/m, -c/m]])
    B = np.array([[0],
                  [1/m]])
    C = np.array([[1, 0]])
    D = np.array([[0]])
    
    return A, B, C, D
