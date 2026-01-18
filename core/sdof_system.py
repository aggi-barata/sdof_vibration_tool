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
    
    @property
    def natural_frequency(self) -> float:
        """Natural frequency ωn in rad/s."""
        return np.sqrt(self.stiffness / self.mass)
    
    @property
    def natural_frequency_hz(self) -> float:
        """Natural frequency fn in Hz."""
        return self.natural_frequency / (2 * np.pi)
    
    @property
    def damping_ratio(self) -> float:
        """Damping ratio ζ (dimensionless)."""
        return self.damping / (2 * np.sqrt(self.stiffness * self.mass))
    
    @property
    def damped_frequency(self) -> float:
        """Damped natural frequency ωd in rad/s."""
        zeta = self.damping_ratio
        if zeta >= 1:
            return 0.0
        return self.natural_frequency * np.sqrt(1 - zeta**2)
    
    @property
    def damped_frequency_hz(self) -> float:
        """Damped natural frequency fd in Hz."""
        return self.damped_frequency / (2 * np.pi)
    
    @property
    def critical_damping(self) -> float:
        """Critical damping coefficient cc in N·s/m."""
        return 2 * np.sqrt(self.stiffness * self.mass)

    @property
    def is_underdamped(self) -> bool:
        """Check if system is underdamped (ζ < 1)."""
        return self.damping_ratio < 1.0

    @property
    def is_critically_damped(self) -> bool:
        """Check if system is critically damped (ζ = 1)."""
        return np.isclose(self.damping_ratio, 1.0, rtol=1e-6)

    @property
    def is_overdamped(self) -> bool:
        """Check if system is overdamped (ζ > 1)."""
        return self.damping_ratio > 1.0

    @classmethod
    def from_damping_ratio(cls, mass: float, stiffness: float, zeta: float) -> "SDOFSystem":
        """Create system from damping ratio instead of damping coefficient.
        
        Args:
            mass: Mass in kg
            stiffness: Stiffness in N/m
            zeta: Damping ratio (dimensionless)
        """
        cc = 2 * np.sqrt(stiffness * mass)
        damping = zeta * cc
        return cls(mass=mass, stiffness=stiffness, damping=damping)
    
    def __str__(self) -> str:
        return (
            f"SDOF System:\n"
            f"  m = {self.mass:.4g} kg\n"
            f"  k = {self.stiffness:.4g} N/m\n"
            f"  c = {self.damping:.4g} N·s/m\n"
            f"  ωn = {self.natural_frequency:.4g} rad/s ({self.natural_frequency_hz:.4g} Hz)\n"
            f"  ζ = {self.damping_ratio:.4g}\n"
            f"  ωd = {self.damped_frequency:.4g} rad/s ({self.damped_frequency_hz:.4g} Hz)"
        )
