"""SDOF system dataclass with derived properties."""

from dataclasses import dataclass
import numpy as np


@dataclass
class SDOFSystem:
    """Single Degree of Freedom vibration system.

    Attributes:
        mass: Mass in kg
        stiffness: Stiffness in N/m
        damping: Damping coefficient in N·s/m
    """
    mass: float
    stiffness: float
    damping: float

    @classmethod
    def from_damping_ratio(cls, mass: float, stiffness: float, zeta: float) -> "SDOFSystem":
        """Create system from damping ratio instead of damping coefficient.

        Args:
            mass: Mass in kg
            stiffness: Stiffness in N/m
            zeta: Damping ratio (dimensionless)

        Returns:
            SDOFSystem instance
        """
        c_critical = 2 * np.sqrt(stiffness * mass)
        damping = zeta * c_critical
        return cls(mass=mass, stiffness=stiffness, damping=damping)

    @property
    def natural_frequency(self) -> float:
        """Undamped natural frequency in rad/s (ωn = √(k/m))."""
        return np.sqrt(self.stiffness / self.mass)

    @property
    def natural_frequency_hz(self) -> float:
        """Undamped natural frequency in Hz (fn = ωn / 2π)."""
        return self.natural_frequency / (2 * np.pi)

    @property
    def critical_damping(self) -> float:
        """Critical damping coefficient (cc = 2√(km))."""
        return 2 * np.sqrt(self.stiffness * self.mass)

    @property
    def damping_ratio(self) -> float:
        """Damping ratio (ζ = c / cc)."""
        return self.damping / self.critical_damping

    @property
    def damped_frequency(self) -> float:
        """Damped natural frequency in rad/s (ωd = ωn√(1-ζ²))."""
        zeta = self.damping_ratio
        if zeta >= 1.0:
            return 0.0
        return self.natural_frequency * np.sqrt(1 - zeta**2)

    @property
    def damped_frequency_hz(self) -> float:
        """Damped natural frequency in Hz."""
        return self.damped_frequency / (2 * np.pi)

    @property
    def is_underdamped(self) -> bool:
        """Check if system is underdamped (ζ < 1)."""
        return self.damping_ratio < 1.0

    @property
    def is_critically_damped(self) -> bool:
        """Check if system is critically damped (ζ = 1)."""
        return np.isclose(self.damping_ratio, 1.0)

    @property
    def is_overdamped(self) -> bool:
        """Check if system is overdamped (ζ > 1)."""
        return self.damping_ratio > 1.0

    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"SDOF System:\n"
            f"  Mass: {self.mass:.4g} kg\n"
            f"  Stiffness: {self.stiffness:.4g} N/m\n"
            f"  Damping: {self.damping:.4g} N·s/m\n"
            f"  Natural freq: {self.natural_frequency:.4g} rad/s ({self.natural_frequency_hz:.4g} Hz)\n"
            f"  Damping ratio: {self.damping_ratio:.4g}\n"
            f"  Damped freq: {self.damped_frequency:.4g} rad/s ({self.damped_frequency_hz:.4g} Hz)"
        )
