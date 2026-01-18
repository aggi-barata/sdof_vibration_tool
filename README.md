# SDOF Vibration Analysis Tool

A web-based tool for analyzing Single Degree of Freedom (SDOF) vibration systems.

**Live Demo:** [https://aggi-barata.github.io/sdof_vibration_tool/](https://aggi-barata.github.io/sdof_vibration_tool/)

## Features

- **Frequency Response Function (FRF)** - Bode plot with magnitude and phase
- **Transmissibility** - Force/displacement transmissibility with multi-damping ratio overlay
- **Time Response** - Impulse, step, harmonic, and free vibration responses
- **Shock Response Spectrum (SRS)** - Analyze transient shock inputs with various pulse types

## System Parameters

| Parameter | Symbol | Unit |
|-----------|--------|------|
| Mass | m | kg |
| Stiffness | k | N/m |
| Damping | c or ζ | N·s/m or ratio |

## Key Equations

**Natural Frequency:**
```
ωn = √(k/m)
fn = ωn / 2π
```

**Damping Ratio:**
```
ζ = c / (2√(km))
```

**Frequency Response Function:**
```
H(ω) = 1 / ((k - mω²) + jcω)
```

**Transmissibility:**
```
TR = √[(1 + (2ζr)²) / ((1 - r²)² + (2ζr)²)]
```
where r = ω/ωn (frequency ratio)

## SRS Pulse Types

- Half Sine
- Versed Sine (Haversine)
- Triangular
- Rectangular
- Trapezoidal
- Initial Peak Sawtooth
- Terminal Peak Sawtooth

## Usage

1. Enter system parameters (mass, stiffness, damping)
2. Select analysis type from tabs
3. Configure analysis options
4. Click "Calculate" to generate plots

## Local Development

Simply open `index.html` in a web browser. No build process required.

The tool also includes Python backend modules in `/core` for numerical computations if needed for more advanced analysis.

## License

MIT
