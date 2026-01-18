"""Control panel for analysis options."""

from typing import Callable, Optional
import customtkinter as ctk


class ControlPanel(ctk.CTkFrame):
    """Panel for analysis type selection and control options."""

    def __init__(
        self,
        parent,
        on_calculate: Optional[Callable[[str], None]] = None,
        on_export_plot: Optional[Callable[[], None]] = None,
        on_export_data: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.on_calculate = on_calculate
        self.on_export_plot = on_export_plot
        self.on_export_data = on_export_data

        self._setup_ui()

    def _setup_ui(self):
        """Set up the control panel UI."""
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Analysis type tabs
        self.analysis_type = ctk.CTkSegmentedButton(
            self,
            values=["Frequency Response", "Transmissibility", "Time Response"],
            command=self._on_analysis_type_changed
        )
        self.analysis_type.set("Frequency Response")
        self.analysis_type.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        # Options frame (changes based on analysis type)
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        self.options_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self._setup_frequency_options()

        # Calculate button
        self.calc_button = ctk.CTkButton(
            self,
            text="Calculate",
            command=self._on_calculate,
            fg_color="#2d7d46",
            hover_color="#236b38"
        )
        self.calc_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Export buttons
        self.export_plot_button = ctk.CTkButton(
            self,
            text="Export Plot",
            command=self._on_export_plot,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a"
        )
        self.export_plot_button.grid(row=2, column=2, padx=5, pady=10, sticky="ew")

        self.export_data_button = ctk.CTkButton(
            self,
            text="Export Data",
            command=self._on_export_data,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a"
        )
        self.export_data_button.grid(row=2, column=3, padx=10, pady=10, sticky="ew")

    def _clear_options(self):
        """Clear the options frame."""
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def _setup_frequency_options(self):
        """Set up frequency response options."""
        self._clear_options()

        ctk.CTkLabel(self.options_frame, text="Freq min (Hz):").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.freq_min_entry = ctk.CTkEntry(self.options_frame, width=80)
        self.freq_min_entry.insert(0, "0.1")
        self.freq_min_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.options_frame, text="Freq max (Hz):").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.freq_max_entry = ctk.CTkEntry(self.options_frame, width=80)
        self.freq_max_entry.insert(0, "100")
        self.freq_max_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.options_frame, text="Points:").grid(
            row=0, column=4, padx=5, pady=5, sticky="e"
        )
        self.n_points_entry = ctk.CTkEntry(self.options_frame, width=80)
        self.n_points_entry.insert(0, "1000")
        self.n_points_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

    def _setup_transmissibility_options(self):
        """Set up transmissibility options."""
        self._clear_options()

        ctk.CTkLabel(self.options_frame, text="Freq min (Hz):").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.freq_min_entry = ctk.CTkEntry(self.options_frame, width=80)
        self.freq_min_entry.insert(0, "0.1")
        self.freq_min_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.options_frame, text="Freq max (Hz):").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.freq_max_entry = ctk.CTkEntry(self.options_frame, width=80)
        self.freq_max_entry.insert(0, "100")
        self.freq_max_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.multi_zeta_var = ctk.BooleanVar(value=False)
        self.multi_zeta_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Show multiple ζ curves",
            variable=self.multi_zeta_var
        )
        self.multi_zeta_check.grid(row=0, column=4, columnspan=2, padx=10, pady=5, sticky="w")

    def _setup_time_options(self):
        """Set up time response options."""
        self._clear_options()

        ctk.CTkLabel(self.options_frame, text="Response:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.time_response_type = ctk.CTkComboBox(
            self.options_frame,
            values=["Impulse", "Step", "Harmonic", "Free Vibration"],
            width=120
        )
        self.time_response_type.set("Impulse")
        self.time_response_type.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.options_frame, text="Duration (s):").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.duration_entry = ctk.CTkEntry(self.options_frame, width=80)
        self.duration_entry.insert(0, "5")
        self.duration_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.options_frame, text="Excitation freq (Hz):").grid(
            row=0, column=4, padx=5, pady=5, sticky="e"
        )
        self.excitation_freq_entry = ctk.CTkEntry(self.options_frame, width=80)
        self.excitation_freq_entry.insert(0, "1.5")
        self.excitation_freq_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

    def _on_analysis_type_changed(self, value: str):
        """Handle analysis type change."""
        if value == "Frequency Response":
            self._setup_frequency_options()
        elif value == "Transmissibility":
            self._setup_transmissibility_options()
        elif value == "Time Response":
            self._setup_time_options()

    def _on_calculate(self):
        """Handle calculate button click."""
        if self.on_calculate:
            self.on_calculate(self.analysis_type.get())

    def _on_export_plot(self):
        """Handle export plot button click."""
        if self.on_export_plot:
            self.on_export_plot()

    def _on_export_data(self):
        """Handle export data button click."""
        if self.on_export_data:
            self.on_export_data()

    def get_analysis_type(self) -> str:
        """Get the selected analysis type."""
        return self.analysis_type.get()

    def get_frequency_range(self) -> tuple[float, float, int]:
        """Get frequency range parameters.

        Returns:
            Tuple of (f_min, f_max, n_points)
        """
        f_min = float(self.freq_min_entry.get())
        f_max = float(self.freq_max_entry.get())
        n_points = int(self.n_points_entry.get()) if hasattr(self, 'n_points_entry') else 1000
        return f_min, f_max, n_points

    def get_time_parameters(self) -> dict:
        """Get time response parameters.

        Returns:
            Dictionary with time response settings
        """
        return {
            "response_type": self.time_response_type.get(),
            "duration": float(self.duration_entry.get()),
            "excitation_freq": float(self.excitation_freq_entry.get())
        }

    def get_multi_zeta(self) -> bool:
        """Get whether to show multiple zeta curves."""
        if hasattr(self, 'multi_zeta_var'):
            return self.multi_zeta_var.get()
        return False
