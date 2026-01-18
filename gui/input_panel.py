"""Parameter input panel for SDOF system."""

from typing import Callable, Optional
import customtkinter as ctk

from core.sdof_system import SDOFSystem
from utils.validators import parse_float, validate_positive, validate_non_negative, ValidationError


class InputPanel(ctk.CTkFrame):
    """Panel for entering SDOF system parameters."""

    def __init__(
        self,
        parent,
        on_system_changed: Optional[Callable[[SDOFSystem], None]] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.on_system_changed = on_system_changed
        self._use_damping_ratio = False

        self._setup_ui()
        self._set_default_values()

    def _setup_ui(self):
        """Set up the input panel UI."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(
            self,
            text="System Parameters",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 15), sticky="w")

        # Mass input
        ctk.CTkLabel(self, text="Mass (kg):").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.mass_entry = ctk.CTkEntry(self, width=120)
        self.mass_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.mass_entry.bind("<KeyRelease>", self._on_parameter_changed)

        # Stiffness input
        ctk.CTkLabel(self, text="Stiffness (N/m):").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.stiffness_entry = ctk.CTkEntry(self, width=120)
        self.stiffness_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.stiffness_entry.bind("<KeyRelease>", self._on_parameter_changed)

        # Damping type toggle
        self.damping_type_var = ctk.StringVar(value="coefficient")
        self.damping_type_switch = ctk.CTkSegmentedButton(
            self,
            values=["Coefficient", "Ratio"],
            command=self._on_damping_type_changed
        )
        self.damping_type_switch.set("Coefficient")
        self.damping_type_switch.grid(row=3, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="ew")

        # Damping input
        self.damping_label = ctk.CTkLabel(self, text="Damping (N·s/m):")
        self.damping_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.damping_entry = ctk.CTkEntry(self, width=120)
        self.damping_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.damping_entry.bind("<KeyRelease>", self._on_parameter_changed)

        # Separator
        separator = ctk.CTkFrame(self, height=2, fg_color="gray50")
        separator.grid(row=5, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

        # Derived values section
        derived_title = ctk.CTkLabel(
            self,
            text="Derived Properties",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        derived_title.grid(row=6, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        # Natural frequency
        ctk.CTkLabel(self, text="ωn (rad/s):").grid(
            row=7, column=0, padx=10, pady=3, sticky="w"
        )
        self.omega_n_label = ctk.CTkLabel(self, text="—")
        self.omega_n_label.grid(row=7, column=1, padx=10, pady=3, sticky="w")

        # Natural frequency Hz
        ctk.CTkLabel(self, text="fn (Hz):").grid(
            row=8, column=0, padx=10, pady=3, sticky="w"
        )
        self.f_n_label = ctk.CTkLabel(self, text="—")
        self.f_n_label.grid(row=8, column=1, padx=10, pady=3, sticky="w")

        # Damping ratio
        ctk.CTkLabel(self, text="ζ:").grid(
            row=9, column=0, padx=10, pady=3, sticky="w"
        )
        self.zeta_label = ctk.CTkLabel(self, text="—")
        self.zeta_label.grid(row=9, column=1, padx=10, pady=3, sticky="w")

        # Damped frequency
        ctk.CTkLabel(self, text="ωd (rad/s):").grid(
            row=10, column=0, padx=10, pady=3, sticky="w"
        )
        self.omega_d_label = ctk.CTkLabel(self, text="—")
        self.omega_d_label.grid(row=10, column=1, padx=10, pady=3, sticky="w")

        # Damping type indicator
        ctk.CTkLabel(self, text="Damping Type:").grid(
            row=11, column=0, padx=10, pady=3, sticky="w"
        )
        self.damping_type_label = ctk.CTkLabel(self, text="—")
        self.damping_type_label.grid(row=11, column=1, padx=10, pady=3, sticky="w")

        # Error message
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            wraplength=200
        )
        self.error_label.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    def _set_default_values(self):
        """Set default parameter values."""
        self.mass_entry.insert(0, "10")
        self.stiffness_entry.insert(0, "1000")
        self.damping_entry.insert(0, "20")
        self._update_derived_values()

    def _on_damping_type_changed(self, value: str):
        """Handle damping type toggle."""
        self._use_damping_ratio = (value == "Ratio")

        if self._use_damping_ratio:
            self.damping_label.configure(text="Damping ratio (ζ):")
            # Convert current coefficient to ratio if valid
            try:
                system = self.get_system()
                self.damping_entry.delete(0, "end")
                self.damping_entry.insert(0, f"{system.damping_ratio:.4g}")
            except (ValidationError, ValueError):
                self.damping_entry.delete(0, "end")
                self.damping_entry.insert(0, "0.1")
        else:
            self.damping_label.configure(text="Damping (N·s/m):")
            # Convert current ratio to coefficient if valid
            try:
                system = self.get_system()
                self.damping_entry.delete(0, "end")
                self.damping_entry.insert(0, f"{system.damping:.4g}")
            except (ValidationError, ValueError):
                self.damping_entry.delete(0, "end")
                self.damping_entry.insert(0, "20")

        self._update_derived_values()

    def _on_parameter_changed(self, event=None):
        """Handle parameter change."""
        self._update_derived_values()

    def _update_derived_values(self):
        """Update derived property labels."""
        self.error_label.configure(text="")

        try:
            system = self.get_system()

            self.omega_n_label.configure(text=f"{system.natural_frequency:.4g}")
            self.f_n_label.configure(text=f"{system.natural_frequency_hz:.4g}")
            self.zeta_label.configure(text=f"{system.damping_ratio:.4g}")
            self.omega_d_label.configure(text=f"{system.damped_frequency:.4g}")

            if system.is_underdamped:
                self.damping_type_label.configure(text="Underdamped")
            elif system.is_critically_damped:
                self.damping_type_label.configure(text="Critically Damped")
            else:
                self.damping_type_label.configure(text="Overdamped")

            if self.on_system_changed:
                self.on_system_changed(system)

        except ValidationError as e:
            self._clear_derived_values()
            self.error_label.configure(text=str(e))
        except ValueError:
            self._clear_derived_values()

    def _clear_derived_values(self):
        """Clear all derived value labels."""
        self.omega_n_label.configure(text="—")
        self.f_n_label.configure(text="—")
        self.zeta_label.configure(text="—")
        self.omega_d_label.configure(text="—")
        self.damping_type_label.configure(text="—")

    def get_system(self) -> SDOFSystem:
        """Get the current SDOF system from inputs.

        Returns:
            SDOFSystem instance

        Raises:
            ValidationError: If inputs are invalid
        """
        mass = parse_float(self.mass_entry.get(), "Mass")
        stiffness = parse_float(self.stiffness_entry.get(), "Stiffness")
        damping_value = parse_float(self.damping_entry.get(), "Damping")

        mass = validate_positive(mass, "Mass")
        stiffness = validate_positive(stiffness, "Stiffness")
        damping_value = validate_non_negative(damping_value, "Damping")

        if self._use_damping_ratio:
            return SDOFSystem.from_damping_ratio(mass, stiffness, damping_value)
        else:
            return SDOFSystem(mass, stiffness, damping_value)

    def set_values(self, mass: float, stiffness: float, damping: float, use_ratio: bool = False):
        """Set parameter values programmatically.

        Args:
            mass: Mass in kg
            stiffness: Stiffness in N/m
            damping: Damping coefficient or ratio
            use_ratio: Whether damping is a ratio
        """
        self.mass_entry.delete(0, "end")
        self.mass_entry.insert(0, str(mass))

        self.stiffness_entry.delete(0, "end")
        self.stiffness_entry.insert(0, str(stiffness))

        if use_ratio != self._use_damping_ratio:
            self.damping_type_switch.set("Ratio" if use_ratio else "Coefficient")
            self._on_damping_type_changed("Ratio" if use_ratio else "Coefficient")

        self.damping_entry.delete(0, "end")
        self.damping_entry.insert(0, str(damping))

        self._update_derived_values()
