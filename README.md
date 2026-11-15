# GERMIN8 Udyam Automation - Starter Project

This ZIP contains a starter project with:
- A business TXT input template
- Optional Gemini AI extraction to JSON
- Basic completeness and format checks
- NIC research-term preparation (does not invent NIC codes)
- Playwright launch and inspection of the actual Udyam portal

## Important: what is and is not implemented

This is **not yet a completed end-to-end registration bot**. The portal module opens the real official portal, inspects basic page elements and saves a screenshot. It does not fill the form. The current live portal must be inspected and verified before implementing field selectors and mapping.

The project does not verify Aadhaar/PAN/GST/bank ownership, bypass OTP/CAPTCHA, submit applications, or guarantee eligibility/approval. Do not click the final Submit button for this assessment.

Use accurate business information only with the owner's permission. Do not put Aadhaar, OTP or bank account numbers in the TXT file, source code, logs, screenshots or recording. Enter sensitive information manually on the official portal when required.

Official portal: https://udyamregistration.gov.in/

## Setup (Windows)

Install Python 3.10+ and then run these commands in the project folder:

```powershell
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
playwright install chromium
```

## Configure Gemini (optional)

1. Visit https://aistudio.google.com/ and obtain an API key if available to your account.
2. Copy `.env.example` to `.env`.
3. Add your key after `GEMINI_API_KEY=`.
4. Never share `.env` or upload it to GitHub.

Without a key, use dry-run mode to test the local setup.

## Prepare and run

Edit `input/business_info.txt` with authorised, accurate information.

Test local input:

```powershell
python main.py --dry-run
```

Run AI extraction:

```powershell
python main.py
```

Outputs are saved in `output/`:
- extracted_data.json
- validation_report.json
- nic_research.json

Open the actual portal for inspection:

```powershell
python main.py --inspect-portal
```

## Next development step

Inspect the current official portal manually, document each applicable field and conditional rule, then implement verified Playwright locators and mappings. Test with authorised data. Pause for manual OTP/CAPTCHA and stop at the final review stage without submitting.

## Recording

Show the TXT file with sensitive values redacted, extraction, validation, NIC research, the real portal opened by Playwright, human verification checkpoints and final review. Do not expose identifiers or OTPs.
