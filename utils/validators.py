"""Input validation utilities."""

from typing import Optional


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_positive(value: float, name: str) -> float:
    """Validate that a value is strictly positive.

    Args:
        value: Value to validate
        name: Parameter name for error message

    Returns:
        Validated value

    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError(f"{name} must be positive (got {value})")
    return value


def validate_non_negative(value: float, name: str) -> float:
    """Validate that a value is non-negative.

    Args:
        value: Value to validate
        name: Parameter name for error message

    Returns:
        Validated value

    Raises:
        ValidationError: If value is negative
    """
    if value < 0:
        raise ValidationError(f"{name} must be non-negative (got {value})")
    return value


def validate_range(
    value: float,
    name: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    min_inclusive: bool = True,
    max_inclusive: bool = True
) -> float:
    """Validate that a value is within a specified range.

    Args:
        value: Value to validate
        name: Parameter name for error message
        min_val: Minimum allowed value (None for no minimum)
        max_val: Maximum allowed value (None for no maximum)
        min_inclusive: Whether minimum is inclusive
        max_inclusive: Whether maximum is inclusive

    Returns:
        Validated value

    Raises:
        ValidationError: If value is outside range
    """
    if min_val is not None:
        if min_inclusive and value < min_val:
            raise ValidationError(f"{name} must be >= {min_val} (got {value})")
        elif not min_inclusive and value <= min_val:
            raise ValidationError(f"{name} must be > {min_val} (got {value})")

    if max_val is not None:
        if max_inclusive and value > max_val:
            raise ValidationError(f"{name} must be <= {max_val} (got {value})")
        elif not max_inclusive and value >= max_val:
            raise ValidationError(f"{name} must be < {max_val} (got {value})")

    return value


def parse_float(text: str, name: str) -> float:
    """Parse a string to float with validation.

    Args:
        text: String to parse
        name: Parameter name for error message

    Returns:
        Parsed float value

    Raises:
        ValidationError: If parsing fails
    """
    text = text.strip()
    if not text:
        raise ValidationError(f"{name} cannot be empty")

    try:
        return float(text)
    except ValueError:
        raise ValidationError(f"{name} must be a valid number (got '{text}')")


def validate_system_parameters(
    mass: float,
    stiffness: float,
    damping: float,
    is_damping_ratio: bool = False
) -> tuple[float, float, float]:
    """Validate complete set of SDOF system parameters.

    Args:
        mass: Mass value
        stiffness: Stiffness value
        damping: Damping coefficient or ratio
        is_damping_ratio: If True, damping is interpreted as ratio

    Returns:
        Tuple of validated (mass, stiffness, damping)

    Raises:
        ValidationError: If any parameter is invalid
    """
    mass = validate_positive(mass, "Mass")
    stiffness = validate_positive(stiffness, "Stiffness")

    if is_damping_ratio:
        damping = validate_non_negative(damping, "Damping ratio")
    else:
        damping = validate_non_negative(damping, "Damping coefficient")

    return mass, stiffness, damping


def validate_frequency_range(
    f_min: float,
    f_max: float,
    n_points: int = 1000
) -> tuple[float, float, int]:
    """Validate frequency range parameters.

    Args:
        f_min: Minimum frequency in Hz
        f_max: Maximum frequency in Hz
        n_points: Number of frequency points

    Returns:
        Tuple of validated (f_min, f_max, n_points)

    Raises:
        ValidationError: If parameters are invalid
    """
    f_min = validate_positive(f_min, "Minimum frequency")
    f_max = validate_positive(f_max, "Maximum frequency")

    if f_max <= f_min:
        raise ValidationError(
            f"Maximum frequency ({f_max}) must be greater than minimum ({f_min})"
        )

    if n_points < 10:
        raise ValidationError(f"Number of points must be at least 10 (got {n_points})")

    if n_points > 100000:
        raise ValidationError(f"Number of points must be at most 100000 (got {n_points})")

    return f_min, f_max, n_points
