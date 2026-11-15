
import json
import time
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


PORTAL_URL = "https://udyamregistration.gov.in/UdyamRegistration.aspx"

SCREENSHOT_DIR = Path("screenshots")
OUTPUT_DIR = Path("output")


def inspect_fields(page):
    """Inspect visible fields without entering or submitting information."""

    results = []

    for selector in ["input", "select", "textarea"]:
        elements = page.locator(selector)

        for i in range(elements.count()):
            element = elements.nth(i)

            try:
                if not element.is_visible():
                    continue

                field_type = element.get_attribute("type") or ""

                if field_type.lower() in ["hidden", "password"]:
                    continue

                results.append({
                    "element": selector,
                    "type": field_type,
                    "id": element.get_attribute("id"),
                    "name": element.get_attribute("name"),
                    "placeholder": element.get_attribute("placeholder"),
                    "aria_label": element.get_attribute("aria-label"),
                    "required": element.get_attribute("required") is not None
                })

            except Exception:
                continue

    return results


def save_inspection(page, stage):
    """Save screenshot and visible field report."""

    SCREENSHOT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    fields = inspect_fields(page)

    report = {
        "stage": stage,
        "page_title": page.title(),
        "page_url": page.url,
        "captured_at": datetime.now().isoformat(),
        "fields": fields
    }

    filename = f"{stage}_inspection.json"

    (OUTPUT_DIR / filename).write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    try:
        page.screenshot(
            path=str(SCREENSHOT_DIR / f"{stage}.png"),
            full_page=True,
            timeout=30000
        )
        print(f"Screenshot saved: screenshots/{stage}.png")

    except Exception as error:
        print("Screenshot error:", error)

    print(f"Report saved: output/{filename}")
    print(f"Visible fields detected: {len(fields)}")

    for field in fields:
        print(field)

    return fields


def is_aadhaar_page(page):
    """Check whether the Aadhaar verification fields are still visible."""

    try:
        aadhaar_field = page.locator(
            "#ctl00_ContentPlaceHolder1_txtadharno"
        )

        name_field = page.locator(
            "#ctl00_ContentPlaceHolder1_txtownername"
        )

        return aadhaar_field.is_visible() and name_field.is_visible()

    except Exception:
        return False


def inspect_portal():

    SCREENSHOT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            viewport={"width": 1366, "height": 900}
        )

        page = context.new_page()

        print("\nGERMIN8 UDYAM PORTAL AUTOMATION")
        print("=" * 45)

        print("\nOpening official Udyam registration page...")

        try:
            page.goto(
                PORTAL_URL,
                wait_until="domcontentloaded",
                timeout=90000
            )

            print("Website connection established.")

        except PlaywrightTimeoutError:
            print("Page loading timed out. Checking current page...")

        except Exception as error:
            print("Website error:", error)
            browser.close()
            return

        page.wait_for_timeout(3000)

        if page.url == "about:blank":
            print("ERROR: Portal did not open.")
            browser.close()
            return

        print("Page title:", page.title())
        print("Current URL:", page.url)

        print("\nSTAGE 1: Aadhaar verification page inspection")

        save_inspection(page, "aadhaar_stage")

        print("\nMANUAL VERIFICATION REQUIRED")
        print("---------------------------------------------")
        print("1. Keep the browser open.")
        print("2. Only an authorised business owner may complete")
        print("   Aadhaar verification directly on the official portal.")
        print("3. Complete any consent and OTP steps yourself.")
        print("4. Do not share Aadhaar or OTP with this program.")
        print("5. Do not proceed to final registration submission.")

        input(
            "\nAfter authorised manual verification, "
            "press Enter here to check the next page.\n"
            "If you have not verified, press Enter to finish."
        )

        print("\nChecking the current browser page...")

        try:
            page.wait_for_timeout(2000)

            print("Current URL:", page.url)
            print("Page title:", page.title())

            if is_aadhaar_page(page):
                print("\nSTAGE 2 NOT REACHED")
                print("The Aadhaar verification fields are still visible.")
                print("No registration form was opened.")
                print("No Stage 2 report will be created.")

            else:
                print("\nSTAGE 2: Registration page inspection")

                fields = save_inspection(
                    page,
                    "registration_stage"
                )

                if len(fields) == 0:
                    print("Warning: No visible form fields detected.")

                else:
                    print("\nRegistration-stage fields inspected.")

        except Exception as error:
            print("Could not inspect the next page:", error)

        print("\nINSPECTION COMPLETED")
        print("=" * 45)
        print("No Aadhaar or OTP values were stored.")
        print("No final registration was submitted.")
        print("Check the output folder for inspection reports.")

        input("\nPress Enter to close the browser...")

        context.close()
        browser.close()


if __name__ == "__main__":
    inspect_portal()
