
def map_portal_fields(data):
    """
    Prepare business information for portal form mapping.
    Sensitive identity fields are deliberately excluded.
    """

    mapped_fields = {
        "enterprise_name": data.get("enterprise_details", {}).get(
            "enterprise_name"
        ),
        "organisation_type": data.get("enterprise_details", {}).get(
            "organisation_type"
        ),
        "commencement_date": data.get("enterprise_details", {}).get(
            "commencement_date"
        ),
        "major_activity": data.get("enterprise_details", {}).get(
            "major_activity"
        ),
        "email": data.get("contact_details", {}).get("email"),
        "mobile": data.get("contact_details", {}).get("mobile"),
        "office_address": data.get("address_details"),
        "units": data.get("unit_details"),
        "employees": data.get("employment_details"),
        "financial_details": data.get("financial_details"),
        "tax_details": data.get("tax_details"),
    }

    missing_fields = [
        key for key, value in mapped_fields.items()
        if value is None or value == ""
    ]

    return {
        "mapped_fields": mapped_fields,
        "missing_fields": missing_fields,
        "manual_review_required": True,
        "sensitive_fields_excluded": [
            "aadhaar",
            "otp",
            "bank_account",
            "final_submission"
        ]
    }
