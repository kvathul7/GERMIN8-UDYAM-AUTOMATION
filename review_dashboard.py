
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
INPUT_DIR = BASE_DIR / "input"
LOG_FILE = OUTPUT_DIR / "activity_log.txt"

BG = "#F4F6FA"
SIDEBAR = "#172554"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
MUTED = "#64748B"
GREEN = "#15803D"
ORANGE = "#B45309"
ACCENT = "#2563EB"


def load_json(filename):
    path = OUTPUT_DIR / filename
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def save_json(filename, data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / filename).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def log_activity(message):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


def flatten_value(value):
    if value is None or value == "":
        return "Not provided"

    if isinstance(value, dict):
        return " | ".join(
            f"{key.replace('_', ' ').title()}: {flatten_value(val)}"
            for key, val in value.items()
        )

    if isinstance(value, list):
        return "\n".join(
            f"• {flatten_value(item)}" for item in value
        ) if value else "Not provided"

    return str(value)


class ReviewDashboard:

    def __init__(self, root):
        self.root = root
        self.root.title("GERMIN8 | Udyam Business Management")
        self.root.geometry("1250x800")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG)

        self.load_data()
        self.setup_styles()
        self.build_layout()
        self.show_dashboard()

    def load_data(self):
        self.portal_data = load_json("portal_ready_data.json")
        self.validation = load_json("validation_report.json")
        self.nic_data = load_json("nic_research.json")
        self.review_status = load_json("review_status.json")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=TEXT,
            rowheight=30,
            fieldbackground=WHITE,
            font=("Segoe UI", 9)
        )

        style.configure(
            "Treeview.Heading",
            background="#E8EEF8",
            foreground=TEXT,
            font=("Segoe UI", 9, "bold")
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=7
        )

    def build_layout(self):
        self.sidebar = tk.Frame(
            self.root, bg=SIDEBAR, width=225
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="GERMIN8",
            font=("Segoe UI", 24, "bold"),
            fg=WHITE,
            bg=SIDEBAR
        ).pack(anchor="w", padx=22, pady=(28, 2))

        tk.Label(
            self.sidebar,
            text="UDYAM AUTOMATION",
            font=("Segoe UI", 9),
            fg="#93C5FD",
            bg=SIDEBAR
        ).pack(anchor="w", padx=24, pady=(0, 35))

        self.add_nav("Dashboard", self.show_dashboard)
        self.add_nav("Business Details", self.show_business)
        self.add_nav("NIC Code Suggestions", self.show_nic)
        self.add_nav("Validation Report", self.show_validation)
        self.add_nav("Activity Log", self.show_activity_log)

        tk.Frame(
            self.sidebar, bg="#334155", height=1
        ).pack(fill="x", padx=18, pady=20)

        tk.Label(
            self.sidebar,
            text="LOCAL REVIEW SYSTEM\n\nAadhaar and OTP are\nnever stored.",
            font=("Segoe UI", 9),
            fg="#CBD5E1",
            bg=SIDEBAR,
            justify="left"
        ).pack(anchor="w", padx=22)

        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(self.main, bg=WHITE, height=65)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Business Registration Workspace",
            font=("Segoe UI", 16, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(side="left", padx=25, pady=17)

        ttk.Button(
            header,
            text="Process Current File",
            command=self.process_current_file
        ).pack(side="right", padx=8)

        ttk.Button(
            header,
            text="Upload Business TXT",
            command=self.upload_business_file
        ).pack(side="right", padx=8)

        ttk.Button(
            header,
            text="Refresh",
            command=self.refresh
        ).pack(side="right", padx=8)

        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True)

    def add_nav(self, label, command):
        tk.Button(
            self.sidebar,
            text="   " + label,
            command=command,
            anchor="w",
            font=("Segoe UI", 10),
            fg="#E2E8F0",
            bg=SIDEBAR,
            activebackground="#334155",
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=13
        ).pack(fill="x", padx=10, pady=2)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def page_heading(self, title, subtitle):
        tk.Label(
            self.content,
            text=title,
            font=("Segoe UI", 21, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w", padx=28, pady=(24, 2))

        tk.Label(
            self.content,
            text=subtitle,
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=BG
        ).pack(anchor="w", padx=29, pady=(0, 18))

    def card(self, parent, title, value, color=ACCENT):
        frame = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )

        tk.Frame(
            frame, bg=color, width=4
        ).pack(side="left", fill="y")

        inner = tk.Frame(frame, bg=WHITE)
        inner.pack(fill="both", expand=True, padx=15, pady=13)

        tk.Label(
            inner, text=title,
            font=("Segoe UI", 9),
            fg=MUTED, bg=WHITE
        ).pack(anchor="w")

        tk.Label(
            inner, text=str(value),
            font=("Segoe UI", 15, "bold"),
            fg=TEXT, bg=WHITE,
            wraplength=180
        ).pack(anchor="w", pady=(5, 0))

        return frame

    def section(self, parent, title):
        frame = tk.Frame(parent, bg=WHITE)
        frame.pack(fill="x", padx=28, pady=7)

        tk.Label(
            frame, text=title,
            font=("Segoe UI", 11, "bold"),
            fg=TEXT, bg=WHITE
        ).pack(anchor="w", padx=17, pady=(13, 9))

        return frame

    def add_table(self, parent, data):
        tree = ttk.Treeview(
            parent,
            columns=("field", "value"),
            show="headings",
            height=min(max(len(data), 2), 10)
        )

        tree.heading("field", text="FIELD")
        tree.heading("value", text="VALUE")
        tree.column("field", width=210, anchor="w")
        tree.column("value", width=600, anchor="w")

        for key, value in data.items():
            tree.insert(
                "",
                "end",
                values=(
                    key.replace("_", " ").title(),
                    flatten_value(value)
                )
            )

        tree.pack(fill="x", padx=15, pady=(0, 15))
        return tree

    def show_dashboard(self):
        self.clear_content()

        self.page_heading(
            "Dashboard",
            "Overview of your Udyam business registration preparation."
        )

        status = self.validation.get("status", "Not available")
        missing = self.validation.get("missing_or_unclear", [])
        approved = self.review_status.get("approved", False)

        status_text = (
            "INTERNAL REVIEW APPROVED"
            if approved else status.upper()
        )

        status_color = GREEN if approved else ORANGE

        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x", padx=28)

        card_data = [
            ("Application Status", status_text, status_color),
            ("Missing Information", len(missing), ORANGE),
            ("NIC Candidates",
             len(self.nic_data.get("candidate_codes", [])), ACCENT),
            ("Review Approval",
             "Yes" if approved else "Pending",
             GREEN if approved else ORANGE)
        ]

        for title, value, color in card_data:
            self.card(cards, title, value, color).pack(
                side="left", fill="both", expand=True, padx=5
            )

        business = self.portal_data.get("enterprise_details", {})
        frame = self.section(self.content, "Business Overview")

        self.add_table(frame, {
            "Enterprise Name": business.get("enterprise_name"),
            "Organisation Type": business.get("organisation_type"),
            "Major Activity": business.get("major_activity"),
            "Commencement Date": business.get("commencement_date")
        })

        frame = self.section(self.content, "Review Information")

        tk.Label(
            frame,
            text="Review extracted information before official registration.",
            bg=WHITE, fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=17, pady=(0, 14))

        actions = tk.Frame(frame, bg=WHITE)
        actions.pack(anchor="w", padx=15, pady=(0, 15))

        ttk.Button(
            actions, text="Edit Business Details",
            command=self.edit_details
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Approve Internal Review",
            command=self.approve_review
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Export PDF",
            command=self.export_pdf
        ).pack(side="left", padx=3)

    def show_business(self):
        self.clear_content()
        self.page_heading(
            "Business Details",
            "Review extracted entrepreneur and enterprise information."
        )

        sections = [
            ("Entrepreneur Details",
             self.portal_data.get("entrepreneur_details", {})),
            ("Enterprise Details",
             self.portal_data.get("enterprise_details", {})),
            ("Office Address",
             self.portal_data.get("address_details", {})),
            ("Contact Details",
             self.portal_data.get("contact_details", {})),
            ("Employment Details",
             self.portal_data.get("employment_details", {})),
            ("Financial Details",
             self.portal_data.get("financial_details", {})),
            ("Tax Details",
             self.portal_data.get("tax_details", {}))
        ]

        for title, data in sections:
            if data:
                frame = self.section(self.content, title)
                self.add_table(frame, data)

        ttk.Button(
            self.content,
            text="Edit Business Information",
            command=self.edit_details
        ).pack(anchor="w", padx=28, pady=15)

    def show_nic(self):
        self.clear_content()
        self.page_heading(
            "NIC Code Suggestions",
            "Suggested classification codes based on business activity."
        )

        codes = self.nic_data.get("candidate_codes", [])

        if not codes:
            self.section(self.content, "No NIC candidates available")
            return

        for code in codes:
            frame = self.section(
                self.content,
                "NIC " + str(code.get("nic_code", "Unknown"))
            )

            self.add_table(frame, {
                "Code": code.get("nic_code"),
                "Description": code.get("description"),
                "Reason": code.get("reason"),
                "Source": code.get("source")
            })

        tk.Label(
            self.content,
            text="NIC suggestions require manual verification.",
            fg=ORANGE, bg=BG,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=30, pady=12)

    def show_validation(self):
        self.clear_content()
        self.page_heading(
            "Validation Report",
            "Review missing or unclear information."
        )

        frame = self.section(self.content, "Validation Summary")
        self.add_table(frame, self.validation)

        missing = self.validation.get("missing_or_unclear", [])
        frame = self.section(self.content, "Missing or Unclear Fields")

        if missing:
            for item in missing:
                tk.Label(
                    frame,
                    text="• " + str(item),
                    bg=WHITE, fg=ORANGE,
                    font=("Segoe UI", 10)
                ).pack(anchor="w", padx=18, pady=4)
        else:
            tk.Label(
                frame,
                text="No missing fields detected by the current validator.",
                bg=WHITE, fg=GREEN
            ).pack(anchor="w", padx=18, pady=12)

    def show_activity_log(self):
        self.clear_content()
        self.page_heading(
            "Activity Log",
            "History of actions performed in the local review application."
        )

        frame = self.section(self.content, "Recorded Activities")

        text = tk.Text(
            frame, height=20,
            font=("Consolas", 10),
            bg="#F8FAFC", fg=TEXT,
            relief="flat", wrap="word"
        )
        text.pack(fill="both", expand=True, padx=15, pady=15)

        if LOG_FILE.exists():
            text.insert("1.0", LOG_FILE.read_text(encoding="utf-8"))
        else:
            text.insert("1.0", "No activity recorded yet.")

        text.config(state="disabled")

    def run_processing(self):
        """Run the existing main.py pipeline and refresh the dashboard."""
        main_file = BASE_DIR / "main.py"

        if not main_file.exists():
            messagebox.showerror(
                "Missing File",
                "main.py was not found in the project folder."
            )
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(main_file)],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=240
            )

            if result.returncode != 0:
                messagebox.showerror(
                    "Processing Failed",
                    (result.stderr or result.stdout or "Unknown error")[-4000:]
                )
                return False

            self.load_data()
            self.review_status = {
                "approved": False,
                "note": "Review reset after processing new business data."
            }
            save_json("review_status.json", self.review_status)

            self.show_dashboard()
            log_activity("Business data processed successfully.")

            messagebox.showinfo(
                "Processing Complete",
                "AI extraction, validation and NIC research completed.\n\n"
                "Check the dashboard and validation report."
            )
            return True

        except subprocess.TimeoutExpired:
            messagebox.showerror(
                "Timeout",
                "Processing took too long. Check Gemini availability."
            )
        except Exception as error:
            messagebox.showerror("Processing Error", str(error))

        return False

    def upload_business_file(self):
        source = filedialog.askopenfilename(
            title="Select Business Information File",
            filetypes=[("Text files", "*.txt")]
        )

        if not source:
            return

        source_path = Path(source).resolve()
        destination = INPUT_DIR / "business_info.txt"

        try:
            INPUT_DIR.mkdir(parents=True, exist_ok=True)

            if source_path == destination.resolve():
                messagebox.showinfo(
                    "Already Selected",
                    "This is already the active business input file.\n\n"
                    "Use Process Current File to run it again."
                )
                return

            if destination.exists():
                replace = messagebox.askyesno(
                    "Replace Existing File?",
                    "This will replace input/business_info.txt.\nContinue?"
                )
                if not replace:
                    return

            shutil.copy2(source_path, destination)
            log_activity("Business TXT file uploaded.")

            messagebox.showinfo(
                "File Uploaded",
                "Business TXT copied successfully.\nStarting processing."
            )

            self.run_processing()

        except Exception as error:
            messagebox.showerror("Upload Error", str(error))

    def process_current_file(self):
        input_file = INPUT_DIR / "business_info.txt"

        if not input_file.exists():
            messagebox.showerror(
                "File Not Found",
                "input/business_info.txt does not exist.\n"
                "Upload a business TXT file first."
            )
            return

        if not messagebox.askyesno(
            "Process Current File",
            "Run AI extraction, validation and NIC research "
            "using the current business file?"
        ):
            return

        self.run_processing()

    def edit_details(self):
        editor = tk.Toplevel(self.root)
        editor.title("Edit Business Information")
        editor.geometry("850x650")

        tk.Label(
            editor,
            text="Edit Business Information JSON",
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=15, pady=12)

        text = tk.Text(
            editor, font=("Consolas", 10), wrap="none"
        )
        text.pack(fill="both", expand=True, padx=15, pady=10)

        text.insert(
            "1.0",
            json.dumps(self.portal_data, indent=2, ensure_ascii=False)
        )

        def save_changes():
            try:
                updated = json.loads(text.get("1.0", "end-1c"))

                if not isinstance(updated, dict):
                    raise ValueError("Expected a JSON object.")

                self.portal_data = updated
                save_json("portal_ready_data.json", updated)

                self.review_status = {
                    "approved": False,
                    "note": "Approval reset after editing."
                }
                save_json("review_status.json", self.review_status)

                log_activity("Business details edited.")
                self.show_dashboard()
                editor.destroy()

                messagebox.showinfo(
                    "Saved",
                    "Business details saved successfully."
                )

            except (json.JSONDecodeError, ValueError) as error:
                messagebox.showerror("Invalid Data", str(error))

        ttk.Button(
            editor, text="Save Changes",
            command=save_changes
        ).pack(pady=12)

    def approve_review(self):
        if not messagebox.askyesno(
            "Confirm Review",
            "Have you manually checked all business information?\n\n"
            "This records internal approval only. It is not "
            "government approval."
        ):
            return

        self.review_status = {
            "approved": True,
            "approved_at": datetime.now().isoformat(),
            "approved_by": "Local reviewer",
            "note": "Internal review only. Not government approval."
        }

        save_json("review_status.json", self.review_status)
        log_activity("Internal review approved.")
        self.show_dashboard()

        messagebox.showinfo(
            "Review Saved",
            "Internal review recorded. This is not government approval."
        )

    def export_pdf(self):
        try:
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Preformatted
            )
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm

        except ImportError:
            messagebox.showerror(
                "Missing Package",
                "Run: pip install reportlab"
            )
            return

        destination = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="GERMIN8_Business_Review.pdf"
        )

        if not destination:
            return

        styles = getSampleStyleSheet()

        story = [
            Paragraph("GERMIN8 - Udyam Business Review", styles["Title"]),
            Spacer(1, 8 * mm),
            Paragraph(
                "INTERNAL REVIEW ONLY - NOT GOVERNMENT APPROVAL",
                styles["Heading2"]
            ),
            Spacer(1, 5 * mm)
        ]

        for section, data in self.portal_data.items():
            if section in ("sensitive_fields_policy", "validation"):
                continue

            story.append(
                Paragraph(
                    section.replace("_", " ").title(),
                    styles["Heading2"]
                )
            )
            story.append(
                Preformatted(
                    json.dumps(data, indent=2, ensure_ascii=False),
                    styles["Code"]
                )
            )
            story.append(Spacer(1, 5 * mm))

        document = SimpleDocTemplate(
            destination,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm
        )

        document.build(story)
        log_activity("PDF review report exported.")

        messagebox.showinfo(
            "PDF Exported",
            "Report saved successfully."
        )

    def refresh(self):
        self.load_data()
        self.show_dashboard()
        log_activity("Dashboard data refreshed.")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    root = tk.Tk()
    app = ReviewDashboard(root)
    root.mainloop()
