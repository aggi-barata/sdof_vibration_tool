# SDOF Vibration Analysis Tool - Technical Documentation

## 1. Introduction

The SDOF (Single Degree of Freedom) Vibration Analysis Tool is a web-based application for analyzing the dynamic behavior of single degree of freedom mechanical systems. It provides comprehensive frequency-domain and time-domain analysis capabilities essential for mechanical engineering, structural dynamics, and vibration isolation design.

## 2. System Model

### 2.1 Equation of Motion

The SDOF system consists of a mass (m), spring (k), and damper (c) subjected to an external force F(t):

```
m·ẍ + c·ẋ + k·x = F(t)
```

Where:
- `x` = displacement (m)
- `ẋ` = velocity (m/s)
- `ẍ` = acceleration (m/s²)
- `m` = mass (kg)
- `k` = stiffness (N/m)
- `c` = damping coefficient (N·s/m)
- `F(t)` = applied force (N)

### 2.2 System Parameters

#### Natural Frequency
The undamped natural frequency represents the frequency at which the system oscillates freely without damping:

```
ωn = √(k/m)  [rad/s]

fn = ωn/(2π)  [Hz]
```

#### Critical Damping
The critical damping coefficient is the minimum damping that prevents oscillation:

```
cc = 2√(km) = 2mωn  [N·s/m]
```

#### Damping Ratio
The damping ratio is a dimensionless measure of damping relative to critical damping:

```
ζ = c/cc = c/(2√(km)) = c/(2mωn)
```

System behavior classification:
- **ζ < 1**: Underdamped (oscillatory response)
- **ζ = 1**: Critically damped (fastest non-oscillatory response)
- **ζ > 1**: Overdamped (slow non-oscillatory response)

#### Damped Natural Frequency
For underdamped systems (ζ < 1), the damped natural frequency is:

```
ωd = ωn√(1 - ζ²)  [rad/s]
```

## 3. Frequency Response Analysis

### 3.1 Frequency Response Function (FRF)

The FRF, also called receptance, relates harmonic displacement output to harmonic force input:

```
H(ω) = X/F = 1/[(k - mω²) + jcω]
```

#### Magnitude
```
|H(ω)| = 1/√[(k - mω²)² + (cω)²]
```

In normalized form using frequency ratio r = ω/ωn:
```
|H(ω)|·k = 1/√[(1 - r²)² + (2ζr)²]
```

#### Phase
```
φ(ω) = -arctan[cω/(k - mω²)] = -arctan[2ζr/(1 - r²)]
```

The phase ranges from 0° at low frequencies to -180° at high frequencies, passing through -90° at resonance.

### 3.2 Dynamic Stiffness

Dynamic stiffness is the inverse of the FRF, representing the force required to produce unit harmonic displacement:

```
K(ω) = F/X = (k - mω²) + jcω
```

#### Magnitude
```
|K(ω)| = √[(k - mω²)² + (cω)²]  [N/m]
```

Key characteristics:
- At ω → 0: |K| → k (static stiffness)
- At ω = ωn: |K| = cωn = 2ζkωn/ωn = 2ζk (minimum for underdamped systems)
- At ω → ∞: |K| → mω² (mass-controlled region)

## 4. Transmissibility Analysis

### 4.1 Force Transmissibility

Transmissibility describes the ratio of transmitted force to applied force (or transmitted displacement to base displacement) for vibration isolation systems:

```
TR = |FT/F| = |XBase/XInput| = √[(1 + (2ζr)²)/((1 - r²)² + (2ζr)²)]
```

Where r = ω/ωn is the frequency ratio.

### 4.2 Key Characteristics

- **At r = 0**: TR = 1 (no isolation)
- **At r = 1** (resonance): TR = √(1 + 4ζ²)/(2ζ) ≈ 1/(2ζ) for light damping
- **At r = √2**: TR = 1 (crossover point, independent of damping)
- **For r > √2**: TR < 1 (isolation region)

### 4.3 Isolation Effectiveness

For effective vibration isolation:
- Operating frequency should be > √2 × natural frequency
- In the isolation region, lower damping provides better isolation
- At resonance, higher damping reduces amplification

## 5. Time Response Analysis

### 5.1 Impulse Response

Response to a unit impulse δ(t) applied at t = 0:

**Underdamped (ζ < 1):**
```
x(t) = (1/mωd)·e^(-ζωnt)·sin(ωdt)
```

**Critically Damped (ζ = 1):**
```
x(t) = (1/m)·t·e^(-ωnt)
```

**Overdamped (ζ > 1):**
```
x(t) = (1/2mωd')·[e^(s₁t) - e^(s₂t)]

where: ωd' = ωn√(ζ² - 1)
       s₁,₂ = -ζωn ± ωd'
```

### 5.2 Step Response

Response to a unit step force F(t) = F₀·u(t):

**Underdamped (ζ < 1):**
```
x(t) = (F₀/k)·[1 - e^(-ζωnt)·(cos(ωdt) + (ζ/√(1-ζ²))·sin(ωdt))]
```

**Critically Damped (ζ = 1):**
```
x(t) = (F₀/k)·[1 - (1 + ωnt)·e^(-ωnt)]
```

**Overdamped (ζ > 1):**
```
x(t) = (F₀/k)·[1 + (s₂·e^(s₁t) - s₁·e^(s₂t))/(s₁ - s₂)]
```

Static deflection: xstatic = F₀/k

### 5.3 Harmonic Response

Response to harmonic excitation F(t) = F₀·sin(ωt):

```
x(t) = xtransient(t) + xsteady(t)
```

**Steady-State Response:**
```
xsteady(t) = X·sin(ωt - φ)

where: X = F₀/√[(k - mω²)² + (cω)²]
       φ = arctan[cω/(k - mω²)]
```

**Transient Response (underdamped):**
```
xtransient(t) = e^(-ζωnt)·[A·cos(ωdt) + B·sin(ωdt)]
```

Coefficients A and B are determined by initial conditions.

### 5.4 Free Vibration

Response with initial displacement x₀ and velocity v₀:

**Underdamped (ζ < 1):**
```
x(t) = e^(-ζωnt)·[x₀·cos(ωdt) + ((v₀ + ζωnx₀)/ωd)·sin(ωdt)]
```

**Decay Envelope:**
```
X(t) = X₀·e^(-ζωnt)
```

The logarithmic decrement (ratio of successive peaks):
```
δ = ln(xn/xn+1) = 2πζ/√(1 - ζ²)
```

### 5.5 Half-Sine Pulse Response

Response to a half-sine acceleration pulse (shock input):

```
a(t) = A₀·sin(πt/τ)  for 0 ≤ t ≤ τ
a(t) = 0             for t > τ
```

Where:
- A₀ = peak acceleration (g or m/s²)
- τ = pulse duration (s)
- Pulse frequency: fp = 1/(2τ)

The response is computed using Newmark-β numerical integration.

### 5.6 Dynamic Stiffness Approach for Half-Sine Pulse Estimation

The dynamic stiffness concept provides a frequency-domain perspective for estimating the peak response to transient shock inputs like half-sine pulses.

#### 5.6.1 Pulse Characterization

A half-sine pulse has a characteristic frequency corresponding to its duration:

```
ωp = π/τ  [rad/s]
fp = 1/(2τ)  [Hz]
```

The pulse can be viewed as a half-cycle of a sinusoidal force at frequency fp.

#### 5.6.2 Equivalent Force

For base acceleration input, the equivalent inertial force on the mass is:

```
F(t) = m·a(t) = m·A₀·sin(πt/τ)

Peak force: Fpeak = m·A₀
```

#### 5.6.3 Dynamic Stiffness at Pulse Frequency

The dynamic stiffness evaluated at the pulse frequency ωp = π/τ:

```
|K(ωp)| = √[(k - m·ωp²)² + (c·ωp)²]
```

In terms of frequency ratio rp = ωp/ωn = fp/fn:

```
|K(ωp)| = k·√[(1 - rp²)² + (2ζrp)²]
```

#### 5.6.4 Peak Displacement Estimate

The peak displacement can be estimated using the dynamic stiffness:

```
xpeak ≈ Fpeak/|K(ωp)| · DSF
```

Where DSF is the Dynamic Shock Factor that accounts for the transient nature of the pulse (typically 1.0 to 2.0 depending on rp).

**Simplified estimate (for engineering purposes):**
```
xpeak ≈ m·A₀/|K(ωp)|
```

#### 5.6.5 Response Regimes Based on Frequency Ratio

The ratio rp = fp/fn determines the response character:

| Frequency Ratio | Regime | Response Characteristic |
|-----------------|--------|------------------------|
| rp << 1 | Quasi-static | Peak response ≈ m·A₀/k (static deflection under peak force) |
| rp ≈ 1 | Resonant | Maximum amplification, xpeak >> m·A₀/k |
| rp >> 1 | Impulsive | Response governed by impulse, xpeak ≈ m·A₀·τ/(m·ωn) |

#### 5.6.6 Dynamic Amplification Factor

The ratio of peak dynamic displacement to equivalent static displacement:

```
DAF = xpeak/(Fpeak/k) = k/|K(ωp)| · DSF
```

For undamped systems at specific frequency ratios:
- rp = 0: DAF = 1.0 (static)
- rp = 1: DAF = 1/(2ζ) (resonance, damping limited)
- rp = 2: DAF ≈ 0.33 (isolation region)

#### 5.6.7 Practical Application

**Step 1:** Calculate the pulse frequency
```
fp = 1/(2τ)
```

**Step 2:** Determine frequency ratio
```
rp = fp/fn = (1/2τ)/(ωn/2π) = π/(τ·ωn)
```

**Step 3:** Calculate dynamic stiffness at pulse frequency
```
|K(ωp)| = k·√[(1 - rp²)² + (2ζrp)²]
```

**Step 4:** Estimate peak displacement
```
xpeak ≈ m·A₀/|K(ωp)|
```

**Step 5:** Convert to peak acceleration response (if needed)
```
apeak_response ≈ ωn²·xpeak
```

#### 5.6.8 Design Implications

1. **If fp < fn (long pulse):** System responds quasi-statically; increase stiffness to reduce displacement

2. **If fp ≈ fn (resonant pulse):** Maximum response; either:
   - Increase damping to limit resonant amplification
   - Modify system to shift fn away from fp

3. **If fp > fn (short pulse):** System provides natural isolation; lower stiffness beneficial

The dynamic stiffness plot in the tool allows visualization of |K(ωp)| across frequencies, enabling quick assessment of system response to various pulse durations.

## 6. Shock Response Spectrum (SRS)

### 6.1 Definition

The SRS represents the peak response of a series of SDOF oscillators (with varying natural frequencies) to a transient input. It characterizes the damage potential of shock events.

### 6.2 Computation Method

For each natural frequency fn in the analysis range:
1. Compute the SDOF response to the base acceleration input
2. Convert relative displacement to pseudo-acceleration: a = ωn²·x
3. Record peak values

### 6.3 SRS Components

- **Primary SRS**: Maximum response during the shock pulse
- **Residual SRS**: Maximum response after the shock pulse ends
- **Maxi-Max SRS**: Absolute maximum of primary and residual (most commonly used)

### 6.4 Q Factor

The quality factor Q relates to damping ratio:
```
Q = 1/(2ζ)
```

Typical values: Q = 10 (ζ = 0.05) is common for SRS analysis per MIL-STD-810.

### 6.5 Supported Pulse Types

| Pulse Type | Waveform |
|------------|----------|
| Half-Sine | a(t) = A₀·sin(πt/τ) |
| Versed Sine | a(t) = A₀·(1 - cos(2πt/τ))/2 |
| Triangular | Linear rise and fall |
| Rectangular | Constant amplitude |
| Trapezoidal | Rise, hold, fall |
| Initial Peak Sawtooth | Linear decay from peak |
| Terminal Peak Sawtooth | Linear rise to peak |

## 7. Numerical Methods

### 7.1 Newmark-β Integration

For time-domain analysis with arbitrary forcing functions, the Newmark-β method is used:

```
x(n+1) = x(n) + Δt·v(n) + Δt²·[(0.5 - β)·a(n) + β·a(n+1)]
v(n+1) = v(n) + Δt·[(1 - γ)·a(n) + γ·a(n+1)]
```

Parameters used (average acceleration method):
- γ = 0.5
- β = 0.25

This method is unconditionally stable and provides second-order accuracy.

### 7.2 Derivative Computation

Velocity and acceleration from displacement use central differences:

**Velocity:**
```
v(i) = [x(i+1) - x(i-1)]/(2Δt)
```

**Acceleration:**
```
a(i) = [x(i+1) - 2x(i) + x(i-1)]/Δt²
```

## 8. Units and Conventions

### 8.1 Input Units

| Parameter | Unit |
|-----------|------|
| Mass | kg |
| Stiffness | N/m |
| Damping coefficient | N·s/m |
| Damping ratio | dimensionless |
| Frequency | Hz |
| Time | s |
| Force | N |
| Acceleration | m/s² or g |

### 8.2 Output Units

| Quantity | Unit |
|----------|------|
| Displacement | mm |
| Velocity | m/s |
| Acceleration | m/s² or g |
| Dynamic Stiffness | N/m |
| FRF Magnitude | dB (ref: static compliance) |
| Phase | degrees |
| Transmissibility | dimensionless |

### 8.3 Sign Conventions

- Positive displacement: direction of positive x-axis
- Phase: negative indicates output lags input
- FRF in dB: 20·log₁₀(|H|·k), normalized by static stiffness

## 9. References

1. Rao, S. S. (2017). *Mechanical Vibrations* (6th ed.). Pearson.
2. Thomson, W. T., & Dahleh, M. D. (2014). *Theory of Vibration with Applications* (5th ed.). Pearson.
3. Harris, C. M., & Piersol, A. G. (2002). *Harris' Shock and Vibration Handbook* (5th ed.). McGraw-Hill.
4. MIL-STD-810H (2019). *Environmental Engineering Considerations and Laboratory Tests*. U.S. Department of Defense.
5. Newmark, N. M. (1959). "A Method of Computation for Structural Dynamics." *Journal of the Engineering Mechanics Division*, ASCE, 85(EM3), 67-94.

---

*Document generated for SDOF Vibration Analysis Tool v1.0*
