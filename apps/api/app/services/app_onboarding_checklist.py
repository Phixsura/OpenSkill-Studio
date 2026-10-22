"""Onboarding checklist — auto-generate checklist based on app type."""

CONNECTOR_CHECKLIST = ["Create app", "Add manifest", "Configure sandbox", "Add secrets", "Add webhook URL", "Submit for review"]
AUTOMATION_CHECKLIST = ["Create app", "Add manifest", "Configure sandbox", "Subscribe to events", "Create automation rules", "Submit for review"]
UI_EXTENSION_CHECKLIST = ["Create app", "Add manifest", "Create UI extension", "Upload entry HTML", "Submit for review"]

def generate_checklist(category: str) -> list[str]:
    checklists = {"connector": CONNECTOR_CHECKLIST, "automation": AUTOMATION_CHECKLIST, "ui_extension": UI_EXTENSION_CHECKLIST}
    return checklists.get(category, CONNECTOR_CHECKLIST)

def compute_progress(checklist: list[str], completed: set[str]) -> dict:
    done = sum(1 for s in checklist if s in completed)
    return {"total": len(checklist), "done": done, "pct": round(done / len(checklist) * 100) if checklist else 0}
