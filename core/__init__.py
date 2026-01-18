"""Core SDOF vibration analysis modules."""

from .sdof_system import SDOFSystem
from .frequency_response import compute_frf
from .transmissibility import compute_transmissibility
from .time_response import (
    compute_impulse_response,
    compute_step_response,
    compute_harmonic_response,
    compute_free_vibration,
    decay_envelope,
)
from .shock_response import compute_srs, compute_srs_from_pulse, generate_shock_pulse

__all__ = [
    "SDOFSystem",
    "compute_frf",
    "compute_transmissibility",
    "compute_impulse_response",
    "compute_step_response",
    "compute_harmonic_response",
    "compute_free_vibration",
    "decay_envelope",
    "compute_srs",
    "compute_srs_from_pulse",
    "generate_shock_pulse",
]
