import re
from typing import Any

PIN_RE = re.compile(r"^[1-9][0-9]{5}$")

def validate(data: dict[str, Any]) -> dict[str, Any]:
    errors, warnings, missing = [], [], []
    for field in ("enterprise_name", "organisation_type", "major_activity"):
        if not data.get(field):
            missing.append(field)

    address = data.get("office_address") or {}
    if isinstance(address, dict):
        pin = address.get("pin_code") or address.get("PIN Code")
        if pin and not PIN_RE.fullmatch(str(pin).strip()):
            errors.append("PIN code must be in six-digit format.")

    mobile = data.get("mobile")
    if mobile:
        digits = re.sub(r"\\D", "", str(mobile))
        if not re.fullmatch(r"[6-9][0-9]{9}", digits):
            errors.append("Mobile number format does not look valid.")

    employees = data.get("employees") or {}
    if isinstance(employees, dict):
        for key in ("male", "female", "other", "total"):
            value = employees.get(key)
            if value is not None:
                try:
                    if int(value) < 0:
                        errors.append(f"Employee count {key} cannot be negative.")
                except (TypeError, ValueError):
                    errors.append(f"Employee count {key} must be a whole number.")

    missing.extend(str(x) for x in data.get("missing_or_unclear", []))
    warnings.extend(str(x) for x in data.get("conflicts", []))
    return {
        "status": "needs_review" if errors or missing or warnings else "format_checks_passed",
        "missing_or_unclear": sorted(set(missing)),
        "errors": errors,
        "warnings": warnings,
        "important_note": "Format checks are not official verification of identity, tax, bank, financial or legal details."
    }
