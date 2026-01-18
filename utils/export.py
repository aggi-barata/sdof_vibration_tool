"""Export utilities for plots and data."""

import csv
from pathlib import Path
from typing import Optional, Union
from datetime import datetime

import numpy as np
from numpy.typing import NDArray
from matplotlib.figure import Figure


def export_plot(
    figure: Figure,
    filepath: Union[str, Path],
    dpi: int = 300,
    transparent: bool = False
) -> Path:
    """Export a matplotlib figure to an image file.

    Args:
        figure: Matplotlib figure to export
        filepath: Output file path (extension determines format)
        dpi: Resolution in dots per inch
        transparent: Whether to use transparent background

    Returns:
        Path to exported file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    figure.savefig(
        filepath,
        dpi=dpi,
        bbox_inches='tight',
        transparent=transparent,
        facecolor='white' if not transparent else 'none'
    )

    return filepath


def export_data(
    filepath: Union[str, Path],
    columns: dict[str, NDArray],
    metadata: Optional[dict] = None
) -> Path:
    """Export numerical data to CSV file.

    Args:
        filepath: Output file path
        columns: Dictionary of column_name -> data_array
        metadata: Optional metadata to include as comments

    Returns:
        Path to exported file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', newline='') as f:
        # Write metadata as comments
        if metadata:
            f.write(f"# SDOF Vibration Analysis Export\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            for key, value in metadata.items():
                f.write(f"# {key}: {value}\n")
            f.write("#\n")

        # Write CSV data
        writer = csv.writer(f)

        # Header row
        headers = list(columns.keys())
        writer.writerow(headers)

        # Data rows
        arrays = [columns[h] for h in headers]
        n_rows = len(arrays[0])

        for i in range(n_rows):
            row = [arr[i] for arr in arrays]
            writer.writerow(row)

    return filepath


def export_frequency_response(
    filepath: Union[str, Path],
    frequencies: NDArray[np.floating],
    magnitude_db: NDArray[np.floating],
    phase_deg: NDArray[np.floating],
    system_info: Optional[dict] = None
) -> Path:
    """Export frequency response data.

    Args:
        filepath: Output file path
        frequencies: Frequency array in Hz
        magnitude_db: Magnitude in dB
        phase_deg: Phase in degrees
        system_info: System parameters for metadata

    Returns:
        Path to exported file
    """
    metadata = system_info or {}
    metadata["Analysis Type"] = "Frequency Response"

    return export_data(
        filepath,
        columns={
            "Frequency (Hz)": frequencies,
            "Magnitude (dB)": magnitude_db,
            "Phase (deg)": phase_deg,
        },
        metadata=metadata
    )


def export_transmissibility(
    filepath: Union[str, Path],
    frequencies: NDArray[np.floating],
    transmissibility: NDArray[np.floating],
    system_info: Optional[dict] = None
) -> Path:
    """Export transmissibility data.

    Args:
        filepath: Output file path
        frequencies: Frequency array in Hz
        transmissibility: TR values
        system_info: System parameters for metadata

    Returns:
        Path to exported file
    """
    metadata = system_info or {}
    metadata["Analysis Type"] = "Transmissibility"

    return export_data(
        filepath,
        columns={
            "Frequency (Hz)": frequencies,
            "Transmissibility": transmissibility,
            "Transmissibility (dB)": 20 * np.log10(transmissibility),
        },
        metadata=metadata
    )


def export_time_response(
    filepath: Union[str, Path],
    time: NDArray[np.floating],
    displacement: NDArray[np.floating],
    response_type: str = "Time Response",
    system_info: Optional[dict] = None
) -> Path:
    """Export time response data.

    Args:
        filepath: Output file path
        time: Time array in seconds
        displacement: Displacement array
        response_type: Type of response for metadata
        system_info: System parameters for metadata

    Returns:
        Path to exported file
    """
    metadata = system_info or {}
    metadata["Analysis Type"] = response_type

    return export_data(
        filepath,
        columns={
            "Time (s)": time,
            "Displacement (m)": displacement,
        },
        metadata=metadata
    )


def generate_export_filename(
    analysis_type: str,
    extension: str = "csv"
) -> str:
    """Generate a timestamped filename for export.

    Args:
        analysis_type: Type of analysis (e.g., "frf", "transmissibility")
        extension: File extension

    Returns:
        Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"sdof_{analysis_type}_{timestamp}.{extension}"
