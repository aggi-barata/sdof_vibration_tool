"""Plot panel with embedded Matplotlib figures."""

from typing import Optional
import customtkinter as ctk
import numpy as np
from numpy.typing import NDArray

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class PlotPanel(ctk.CTkFrame):
    """Panel for displaying Matplotlib plots."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the plot panel UI."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create figure with two subplots (for magnitude and phase)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.set_facecolor('#2b2b2b')

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Create toolbar frame
        toolbar_frame = ctk.CTkFrame(self)
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))

        # Navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        # Initial empty plot
        self._setup_default_axes()

    def _setup_default_axes(self):
        """Set up default axes configuration."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_color('white')
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Magnitude")
        ax.grid(True, alpha=0.3)
        ax.text(
            0.5, 0.5,
            "Enter parameters and click Calculate",
            transform=ax.transAxes,
            ha='center', va='center',
            fontsize=12,
            color='gray'
        )
        self.canvas.draw()

    def _style_axis(self, ax, xlabel: str = "", ylabel: str = "", title: str = ""):
        """Apply consistent styling to an axis."""
        ax.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_color('white')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

    def plot_frequency_response(
        self,
        frequencies: NDArray[np.floating],
        magnitude_db: NDArray[np.floating],
        phase_deg: NDArray[np.floating],
        natural_freq_hz: Optional[float] = None
    ):
        """Plot frequency response (Bode plot).

        Args:
            frequencies: Frequency array in Hz
            magnitude_db: Magnitude in dB
            phase_deg: Phase in degrees
            natural_freq_hz: Natural frequency for vertical line marker
        """
        self.figure.clear()

        # Magnitude plot
        ax1 = self.figure.add_subplot(211)
        self._style_axis(ax1, ylabel="Magnitude (dB)", title="Frequency Response")
        ax1.semilogx(frequencies, magnitude_db, 'c-', linewidth=1.5)

        if natural_freq_hz:
            ax1.axvline(natural_freq_hz, color='r', linestyle='--', alpha=0.7, label=f'fn = {natural_freq_hz:.2f} Hz')
            ax1.legend(loc='upper right', facecolor='#2b2b2b', labelcolor='white')

        # Phase plot
        ax2 = self.figure.add_subplot(212, sharex=ax1)
        self._style_axis(ax2, xlabel="Frequency (Hz)", ylabel="Phase (deg)")
        ax2.semilogx(frequencies, phase_deg, 'c-', linewidth=1.5)

        if natural_freq_hz:
            ax2.axvline(natural_freq_hz, color='r', linestyle='--', alpha=0.7)

        ax2.set_yticks([-180, -135, -90, -45, 0])

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_transmissibility(
        self,
        frequencies: NDArray[np.floating],
        transmissibility: NDArray[np.floating],
        zeta: float,
        natural_freq_hz: Optional[float] = None,
        multi_zeta: Optional[list[tuple[float, NDArray]]] = None
    ):
        """Plot transmissibility.

        Args:
            frequencies: Frequency array in Hz
            transmissibility: TR values
            zeta: Damping ratio
            natural_freq_hz: Natural frequency for reference
            multi_zeta: Optional list of (zeta, TR) tuples for multiple curves
        """
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        self._style_axis(ax, xlabel="Frequency (Hz)", ylabel="Transmissibility", title="Transmissibility")

        if multi_zeta:
            colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(multi_zeta)))
            for (z, tr), color in zip(multi_zeta, colors):
                ax.semilogy(frequencies, tr, color=color, linewidth=1.5, label=f'ζ = {z:.2f}')
            ax.legend(loc='upper right', facecolor='#2b2b2b', labelcolor='white')
        else:
            ax.semilogy(frequencies, transmissibility, 'c-', linewidth=1.5, label=f'ζ = {zeta:.3f}')
            ax.legend(loc='upper right', facecolor='#2b2b2b', labelcolor='white')

        # TR = 1 reference line
        ax.axhline(1.0, color='yellow', linestyle='--', alpha=0.5, label='TR = 1')

        if natural_freq_hz:
            # Isolation starts at sqrt(2) * fn
            isolation_start = np.sqrt(2) * natural_freq_hz
            ax.axvline(isolation_start, color='r', linestyle=':', alpha=0.7)
            ax.annotate(
                f'Isolation starts\n({isolation_start:.1f} Hz)',
                xy=(isolation_start, 1),
                xytext=(isolation_start * 1.5, 2),
                arrowprops=dict(arrowstyle='->', color='white', alpha=0.7),
                color='white',
                fontsize=9
            )

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_time_response(
        self,
        time: NDArray[np.floating],
        displacement: NDArray[np.floating],
        response_type: str = "Time Response",
        envelope: Optional[NDArray[np.floating]] = None
    ):
        """Plot time-domain response.

        Args:
            time: Time array in seconds
            displacement: Displacement array
            response_type: Type of response for title
            envelope: Optional decay envelope to overlay
        """
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        self._style_axis(ax, xlabel="Time (s)", ylabel="Displacement (m)", title=response_type)

        ax.plot(time, displacement, 'c-', linewidth=1.5, label='Response')

        if envelope is not None:
            ax.plot(time, envelope, 'r--', linewidth=1, alpha=0.7, label='Decay envelope')
            ax.plot(time, -envelope, 'r--', linewidth=1, alpha=0.7)
            ax.legend(loc='upper right', facecolor='#2b2b2b', labelcolor='white')

        ax.axhline(0, color='white', linewidth=0.5, alpha=0.3)

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_harmonic_response(
        self,
        time: NDArray[np.floating],
        displacement: NDArray[np.floating],
        excitation_freq: float,
        steady_state_amplitude: float
    ):
        """Plot harmonic excitation response.

        Args:
            time: Time array in seconds
            displacement: Displacement array
            excitation_freq: Excitation frequency in Hz
            steady_state_amplitude: Steady-state amplitude for reference
        """
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        self._style_axis(
            ax,
            xlabel="Time (s)",
            ylabel="Displacement (m)",
            title=f"Harmonic Response (f = {excitation_freq:.2f} Hz)"
        )

        ax.plot(time, displacement, 'c-', linewidth=1.5)

        # Steady-state amplitude lines
        ax.axhline(steady_state_amplitude, color='r', linestyle='--', alpha=0.5, label=f'Steady-state: ±{steady_state_amplitude:.4g} m')
        ax.axhline(-steady_state_amplitude, color='r', linestyle='--', alpha=0.5)
        ax.axhline(0, color='white', linewidth=0.5, alpha=0.3)

        ax.legend(loc='upper right', facecolor='#2b2b2b', labelcolor='white')

        self.figure.tight_layout()
        self.canvas.draw()

    def get_figure(self) -> Figure:
        """Get the matplotlib figure for export.

        Returns:
            Matplotlib Figure object
        """
        return self.figure

    def clear(self):
        """Clear the plot."""
        self._setup_default_axes()
