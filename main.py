
import argparse
import json
import sys

from src.config import INPUT_FILE, OUTPUT_DIR
from src.ai_extractor import read_input, extract_business_data
from src.validator import validate
from src.nic_mapper import prepare_nic_research


def save_json(filename, data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_path = OUTPUT_DIR / filename

    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Saved: output/{filename}")


def normalize_activity_descriptions(value):
    """
    Convert activity descriptions into a clean list of strings.
    Gemini may return either one string or a list.
    """

    if isinstance(value, str):
        activities = [value]

    elif isinstance(value, list):
        activities = value

    else:
        activities = []

    return [
        item.strip()
        for item in activities
        if isinstance(item, str) and item.strip()
    ]


def prepare_portal_data(extracted, validation, nic):
    return {
        "application_type": "New Udyam Registration",

        "entrepreneur_details": {
            "name": extracted.get("entrepreneur_name"),
            "date_of_birth": extracted.get("date_of_birth"),
            "gender": extracted.get("gender"),
            "social_category": extracted.get("social_category"),
            "differently_abled": extracted.get("differently_abled")
        },

        "enterprise_details": {
            "enterprise_name": extracted.get("enterprise_name"),
            "organisation_type": extracted.get("organisation_type"),
            "commencement_date": extracted.get("commencement_date"),
            "major_activity": extracted.get("major_activity"),
            "activity_descriptions": normalize_activity_descriptions(
                extracted.get("activity_descriptions")
            ),
            "existing_nic_codes": extracted.get("existing_nic_codes"),
            "suggested_nic_codes": nic.get("candidate_codes", [])
        },

        "address_details": extracted.get("office_address"),

        "unit_details": extracted.get("units"),

        "contact_details": {
            "email": extracted.get("email"),
            "mobile": extracted.get("mobile")
        },

        "employment_details": extracted.get("employees"),

        "financial_details": {
            "investment": extracted.get("investment"),
            "turnover": extracted.get("turnover"),
            "export_turnover": extracted.get("export_turnover"),
            "financial_year": extracted.get("financial_year")
        },

        "tax_details": {
            "pan_available": extracted.get("pan_available"),
            "gstin_status": extracted.get("gstin_status"),
            "itr_filed": extracted.get("itr_filed")
        },

        "previous_registration": extracted.get("previous_udyam"),

        "validation": validation,

        "manual_review_required": True,

        "sensitive_fields_policy": {
            "aadhaar": "Manual entry only",
            "otp": "Manual entry only",
            "bank_account": "Not stored",
            "final_registration_submission": "Manual only"
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="GERMIN8 Udyam Business Registration Automation"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check input file without calling Gemini"
    )

    parser.add_argument(
        "--inspect-portal",
        action="store_true",
        help="Inspect the official Udyam portal"
    )

    args = parser.parse_args()

    if args.inspect_portal:
        from src.portal import inspect_portal
        inspect_portal()
        return

    print("\nGERMIN8 UDYAM AUTOMATION")
    print("=" * 45)

    try:
        # STEP 1: Read input
        print("\nStep 1: Reading business information...")

        source = read_input(INPUT_FILE)

        if not source.strip():
            raise ValueError("Business information file is empty.")

        if args.dry_run:
            print(f"Input read successfully: {len(source)} characters")
            print("Dry run completed. Gemini was not called.")
            return

        # STEP 2: AI extraction
        print("\nStep 2: Extracting business information...")

        extracted = extract_business_data(source)

        if not isinstance(extracted, dict):
            raise ValueError("Gemini did not return a valid JSON object.")

        # Normalize activity descriptions before NIC research
        activities = normalize_activity_descriptions(
            extracted.get("activity_descriptions")
        )

        extracted["activity_descriptions"] = activities

        print("AI extraction completed.")
        print("Activities detected:", activities)

        # STEP 3: Validation
        print("\nStep 3: Validating business information...")

        report = validate(extracted)

        print("Validation completed.")

        # STEP 4: NIC research
        print("\nStep 4: Researching NIC code candidates...")

        nic = prepare_nic_research(activities)

        print("NIC research completed.")
        print(
            "NIC candidates found:",
            len(nic.get("candidate_codes", []))
        )

        # STEP 5: Prepare portal data
        print("\nStep 5: Preparing portal-ready data...")

        portal_data = prepare_portal_data(
            extracted,
            report,
            nic
        )

        # STEP 6: Prepare field mapping
        print("\nStep 6: Mapping portal fields...")

        try:
            from src.field_mapper import map_portal_fields
            field_mapping = map_portal_fields(portal_data)

        except ImportError:
            # Keep the pipeline running if the optional mapper
            # module is not present in the project.
            field_mapping = {
                "mapped_fields": portal_data,
                "manual_review_required": True,
                "sensitive_fields_excluded": [
                    "aadhaar",
                    "otp",
                    "bank_account",
                    "final_submission"
                ]
            }

        # STEP 7: Save output
        print("\nSaving output files...")

        save_json("extracted_data.json", extracted)
        save_json("validation_report.json", report)
        save_json("nic_research.json", nic)
        save_json("portal_ready_data.json", portal_data)
        save_json("portal_field_mapping.json", field_mapping)

        print("\n" + "=" * 45)
        print("PROCESS COMPLETED")
        print("=" * 45)

        print("\nVALIDATION REPORT:")
        print(json.dumps(report, indent=2, ensure_ascii=False))

        print("\nNIC RESEARCH SUMMARY:")
        print(json.dumps(nic, indent=2, ensure_ascii=False))

        print("\nAll output files generated successfully.")
        print("Manual review is required before portal interaction.")
        print("Aadhaar and OTP remain manual.")
        print("No final registration submission was performed.")

    except FileNotFoundError as error:
        print("\nINPUT FILE ERROR:", error)
        sys.exit(1)

    except Exception as error:
        print("\nPROCESSING ERROR:", type(error).__name__)
        print(str(error))
        sys.exit(1)


if __name__ == "__main__":
    main()
