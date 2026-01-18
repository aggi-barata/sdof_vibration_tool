"""Main application window for SDOF Vibration Analysis Tool."""
from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk
import numpy as np

from core.sdof_system import SDOFSystem
from core.frequency_response import compute_frf
from core.transmissibility import compute_transmissibility, compute_transmissibility_normalized
from core.time_response import (
    compute_impulse_response,
    compute_step_response,
    compute_harmonic_response,
    compute_free_vibration,
    decay_envelope
)
from utils.validators import ValidationError
from utils.export import export_plot, export_frequency_response, export_transmissibility, export_time_response

from .input_panel import InputPanel
from .plot_panel import PlotPanel
from .control_panel import ControlPanel


class SDOFApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("SDOF Vibration Analysis Tool")
        self.geometry("1200x800")
        self.minsize(900, 600)

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Current system and data
        self._system: SDOFSystem | None = None
        self._current_data: dict | None = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the main UI layout."""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Input panel - fixed width
        self.grid_columnconfigure(1, weight=1)  # Plot panel - expandable

        # Left panel: inputs
        left_frame = ctk.CTkFrame(self, width=280)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_propagate(False)

        self.input_panel = InputPanel(
            left_frame,
            on_system_changed=self._on_system_changed
        )
        self.input_panel.pack(fill="both", expand=True, padx=5, pady=5)

        # Right panel: plot and controls
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Plot panel
        self.plot_panel = PlotPanel(right_frame)
        self.plot_panel.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Control panel
        self.control_panel = ControlPanel(
            right_frame,
            on_calculate=self._on_calculate,
            on_export_plot=self._on_export_plot,
            on_export_data=self._on_export_data
        )
        self.control_panel.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    def _on_system_changed(self, system: SDOFSystem):
        """Handle system parameter changes."""
        self._system = system

    def _on_calculate(self, analysis_type: str):
        """Handle calculate button click."""
        try:
            system = self.input_panel.get_system()
            self._system = system

            if analysis_type == "Frequency Response":
                self._calculate_frequency_response()
            elif analysis_type == "Transmissibility":
                self._calculate_transmissibility()
            elif analysis_type == "Time Response":
                self._calculate_time_response()

        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def _calculate_frequency_response(self):
        """Calculate and plot frequency response."""
        f_min, f_max, n_points = self.control_panel.get_frequency_range()
        frequencies = np.logspace(np.log10(f_min), np.log10(f_max), n_points)

        magnitude_db, phase_deg, H = compute_frf(self._system, frequencies)

        self._current_data = {
            "type": "frequency_response",
            "frequencies": frequencies,
            "magnitude_db": magnitude_db,
            "phase_deg": phase_deg
        }

        self.plot_panel.plot_frequency_response(
            frequencies,
            magnitude_db,
            phase_deg,
            natural_freq_hz=self._system.natural_frequency_hz
        )

    def _calculate_transmissibility(self):
        """Calculate and plot transmissibility."""
        f_min, f_max, _ = self.control_panel.get_frequency_range()
        frequencies = np.linspace(f_min, f_max, 500)

        if self.control_panel.get_multi_zeta():
            # Multiple zeta curves
            zeta_values = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
            r = frequencies / self._system.natural_frequency_hz

            multi_curves = []
            for z in zeta_values:
                tr = compute_transmissibility_normalized(z, r)
                multi_curves.append((z, tr))

            self._current_data = {
                "type": "transmissibility_multi",
                "frequencies": frequencies,
                "curves": multi_curves
            }

            self.plot_panel.plot_transmissibility(
                frequencies,
                multi_curves[0][1],  # First curve for reference
                self._system.damping_ratio,
                natural_freq_hz=self._system.natural_frequency_hz,
                multi_zeta=multi_curves
            )
        else:
            transmissibility = compute_transmissibility(self._system, frequencies)

            self._current_data = {
                "type": "transmissibility",
                "frequencies": frequencies,
                "transmissibility": transmissibility
            }

            self.plot_panel.plot_transmissibility(
                frequencies,
                transmissibility,
                self._system.damping_ratio,
                natural_freq_hz=self._system.natural_frequency_hz
            )

    def _calculate_time_response(self):
        """Calculate and plot time response."""
        params = self.control_panel.get_time_parameters()
        duration = params["duration"]
        n_points = int(duration * 1000)  # 1 ms resolution
        time = np.linspace(0, duration, n_points)

        response_type = params["response_type"]

        if response_type == "Impulse":
            displacement = compute_impulse_response(self._system, time)
            env = decay_envelope(self._system, time, np.max(np.abs(displacement)))

            self._current_data = {
                "type": "time_response",
                "response_type": "Impulse Response",
                "time": time,
                "displacement": displacement
            }

            self.plot_panel.plot_time_response(
                time, displacement, "Impulse Response", envelope=env
            )

        elif response_type == "Step":
            displacement = compute_step_response(self._system, time)

            self._current_data = {
                "type": "time_response",
                "response_type": "Step Response",
                "time": time,
                "displacement": displacement
            }

            self.plot_panel.plot_time_response(time, displacement, "Step Response")

        elif response_type == "Harmonic":
            excitation_freq = params["excitation_freq"]
            displacement = compute_harmonic_response(
                self._system, time, excitation_freq
            )

            # Calculate steady-state amplitude
            omega = 2 * np.pi * excitation_freq
            m, k, c = self._system.mass, self._system.stiffness, self._system.damping
            steady_amp = 1.0 / np.sqrt((k - m * omega**2)**2 + (c * omega)**2)

            self._current_data = {
                "type": "time_response",
                "response_type": f"Harmonic Response (f={excitation_freq} Hz)",
                "time": time,
                "displacement": displacement
            }

            self.plot_panel.plot_harmonic_response(
                time, displacement, excitation_freq, steady_amp
            )

        elif response_type == "Free Vibration":
            displacement = compute_free_vibration(
                self._system, time, initial_displacement=1.0, initial_velocity=0.0
            )
            env = decay_envelope(self._system, time, 1.0)

            self._current_data = {
                "type": "time_response",
                "response_type": "Free Vibration",
                "time": time,
                "displacement": displacement
            }

            self.plot_panel.plot_time_response(
                time, displacement, "Free Vibration (x₀=1, v₀=0)", envelope=env
            )

    def _on_export_plot(self):
        """Export current plot to image file."""
        if self._current_data is None:
            messagebox.showwarning("No Data", "Please calculate first before exporting.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("PDF Document", "*.pdf"),
                ("SVG Vector", "*.svg")
            ],
            title="Export Plot"
        )

        if filepath:
            try:
                export_plot(self.plot_panel.get_figure(), filepath)
                messagebox.showinfo("Success", f"Plot exported to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def _on_export_data(self):
        """Export current data to CSV file."""
        if self._current_data is None:
            messagebox.showwarning("No Data", "Please calculate first before exporting.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv")],
            title="Export Data"
        )

        if not filepath:
            return

        try:
            system_info = {
                "Mass (kg)": self._system.mass,
                "Stiffness (N/m)": self._system.stiffness,
                "Damping (N·s/m)": self._system.damping,
                "Natural freq (Hz)": self._system.natural_frequency_hz,
                "Damping ratio": self._system.damping_ratio
            }

            data_type = self._current_data["type"]

            if data_type == "frequency_response":
                export_frequency_response(
                    filepath,
                    self._current_data["frequencies"],
                    self._current_data["magnitude_db"],
                    self._current_data["phase_deg"],
                    system_info
                )
            elif data_type in ("transmissibility", "transmissibility_multi"):
                export_transmissibility(
                    filepath,
                    self._current_data["frequencies"],
                    self._current_data.get("transmissibility", self._current_data.get("curves", [(0, [])])[0][1]),
                    system_info
                )
            elif data_type == "time_response":
                export_time_response(
                    filepath,
                    self._current_data["time"],
                    self._current_data["displacement"],
                    self._current_data["response_type"],
                    system_info
                )

            messagebox.showinfo("Success", f"Data exported to:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))


def run():
    """Run the application."""
    app = SDOFApp()
    app.mainloop()
