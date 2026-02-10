from .models import RotVerdict

def generate_report(verdicts: list[RotVerdict]) -> str:
    """Generates the Markdown report/PR description."""

    actionable_verdicts = [v for v in verdicts if v.suggested_action != 'NONE']

    if not actionable_verdicts:
        return "No actionable items found. Repository is clean."

    report = "# [Entropy] Maintenance - Liability Reduction\n\n"
    report += "| File | Rot Type | Unique Coverage | Action Taken | Rationale |\n"
    report += "|---|---|---|---|---|\n"

    for v in actionable_verdicts:
        file = v.file
        rot_type = ", ".join(v.tags) if v.tags else "N/A"
        unique_cov = f"{v.unique_coverage} lines"
        action = v.suggested_action
        rationale = v.rationale

        report += f"| {file} | {rot_type} | {unique_cov} | {action} | {rationale} |\n"

    return report

def generate_summary(verdicts: list[RotVerdict]) -> str:
    """Generates a short summary."""
    total = len(verdicts)
    actions = len([v for v in verdicts if v.suggested_action != 'NONE'])
    return f"Scanned {total} files. {actions} actions suggested/taken."
