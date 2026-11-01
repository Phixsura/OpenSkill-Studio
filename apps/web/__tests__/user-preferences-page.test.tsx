import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UserPreferencesPage } from "@/components/user-preferences-page";

const prefs = { theme: "system", language: "en", notificationsEnabled: true, emailDigest: "weekly", defaultView: "grid", showBeta: false, autoUpdate: true };

describe("UserPreferencesPage", () => {
  it("renders preferences", () => {
    const { container } = render(<UserPreferencesPage prefs={prefs} />);
    expect(container.textContent).toContain("Preferences");
    expect(container.textContent).toContain("Theme");
    expect(container.textContent).toContain("Show beta");
  });
  it("save preferences", () => {
    const fn = vi.fn();
    const { container } = render(<UserPreferencesPage prefs={prefs} onSave={fn} />);
    const saveBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Save Preferences");
    if (saveBtn) fireEvent.click(saveBtn);
    expect(fn).toHaveBeenCalled();
  });
});
