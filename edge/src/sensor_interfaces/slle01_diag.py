#!/usr/bin/env python3
from sensor_SLLE01_modbus import SLLE01

def main():
    s = SLLE01(debug=True)

    unit = s.read_register(2, 0, 3, signed=False)
    dp   = s.read_register(3, 0, 3, signed=False)

    # Read measurement using the device's own decimal-point configuration
    raw = s.read_register(4, int(dp), 3, signed=True)

    print("\n--- SLLE01 DIAG ---")
    print(f"unit_code (reg2): {unit}")
    print(f"decimal_points (reg3): {dp}")
    print(f"measurement (reg4) using dp={dp}: {raw}")

    # Interpretations:
    # If raw is kPa => level_cm = kPa * 10.197
    level_cm_from_kpa = raw * 10.197
    # If raw is cm => level_cm = raw
    level_cm_from_cm  = raw
    # If raw is mm => level_cm = raw / 10
    level_cm_from_mm  = raw / 10.0

    print("\nInterpretations:")
    print(f"Assume kPa: level ≈ {level_cm_from_kpa:.2f} cm")
    print(f"Assume cm : level ≈ {level_cm_from_cm:.2f} cm")
    print(f"Assume mm : level ≈ {level_cm_from_mm:.2f} cm")

if __name__ == "__main__":
    main()
