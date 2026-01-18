# SDOF Vibration Analysis Tool

A web-based tool for analyzing Single Degree of Freedom (SDOF) vibration systems.

**Live Demo:** [https://aggi-barata.github.io/sdof_vibration_tool/](https://aggi-barata.github.io/sdof_vibration_tool/)

## Features

### Frequency Response Function (FRF)
Bode plot showing magnitude (dB) and phase response across frequency range. Displays resonance peak at natural frequency.

### Transmissibility
Force/displacement transmissibility vs frequency with optional multi-damping ratio overlay. Shows the classic √2 crossover point.

### Time Response
Multiple excitation types with analytical solutions and Newmark-beta numerical integration:

| Response Type | Description | Input |
|---------------|-------------|-------|
| **Impulse** | Response to instantaneous impulse, shows decay envelope | Impulse (N·s) |
| **Step** | Response to sudden constant force application | Force (N) |
| **Harmonic** | Steady-state + transient response to sinusoidal excitation | Force (N), Frequency (Hz) |
| **Ramp Force** | Linear force ramp to constant value | Force (N), Ramp time (s) |
| **Swept Sine (Chirp)** | Frequency sweep for resonance identification | Force (N), Start/End freq (Hz) |
| **Half-Sine Pulse** | Shock pulse response with configurable duration | Shock level (g), Duration (ms) |
| **Free Vibration** | Natural response from initial conditions | x₀ (m), v₀ (m/s) |

#### Design Constraint
- **Max Allowable Displacement**: Set a displacement limit to verify design compliance
- Visual indication when response exceeds the limit (lines turn red)
- Warning displayed in plot subtitle with actual vs. allowable values

### Shock Response Spectrum (SRS)
Analyze peak response of oscillators across frequency range when subjected to transient shock. Supports maxi-max, primary, and residual spectra.

## System Parameters

| Parameter | Symbol | Unit |
|-----------|--------|------|
| Mass | m | kg |
| Stiffness | k | N/m |
| Damping | c or ζ | N·s/m or ratio |

### Derived Properties
- Natural frequency: ωn, fn
- Damping ratio: ζ
- Damped frequency: ωd
- Damping classification (underdamped/critically damped/overdamped)

## Damping Regimes

The tool properly handles all three damping regimes:

| Regime | Condition | Behavior |
|--------|-----------|----------|
| **Underdamped** | ζ < 1 | Oscillatory decay with damped frequency ωd = ωn√(1-ζ²) |
| **Critically Damped** | ζ = 1 | Fastest non-oscillatory return to equilibrium |
| **Overdamped** | ζ > 1 | Slow non-oscillatory decay (two real exponential terms) |

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

**Damped Frequency:**
```
ωd = ωn√(1 - ζ²)    (for ζ < 1)
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

| Pulse Type | Description |
|------------|-------------|
| Half Sine | Most common shock test waveform |
| Versed Sine | Haversine pulse, smoother onset |
| Triangular | Isosceles triangle pulse |
| Rectangular | Square pulse |
| Trapezoidal | Pulse with rise/hold/fall phases |
| Initial Peak Sawtooth | Starts at peak, decays linearly |
| Terminal Peak Sawtooth | Ramps up to peak at end |

### SRS Damping Factor (Q)
SRS uses Q (quality factor) rather than damping ratio:
```
Q = 1 / (2ζ)
```
Standard value: Q = 10 (ζ = 0.05)

## Usage

1. Enter system parameters (mass, stiffness, damping)
2. Select analysis type from tabs
3. Configure analysis-specific options
4. Set max allowable displacement constraint (optional)
5. Click "Calculate" to generate plots
6. Use plot toolbar to zoom, pan, reset axes, or export

## Local Development

Simply open `index.html` in a web browser. No build process required.

The tool also includes Python backend modules in `/core` for numerical computations if needed for more advanced analysis.

## Technical Details

- **Frontend:** Vanilla JavaScript with Plotly.js for interactive plotting
- **Numerical Methods:**
  - Analytical solutions for impulse, step, harmonic, and free vibration
  - Newmark-beta integration (average acceleration method) for ramp, chirp, and half-sine pulse
- **Damping:** Full support for underdamped, critically damped, and overdamped systems
- **No dependencies:** Runs entirely in the browser

## License

MIT
