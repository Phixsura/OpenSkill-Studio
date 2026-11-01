import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UserPreferencesForm } from "@/components/user-preferences-form";

describe("UserPreferencesForm", () => {
  const prefs = { theme: "dark", language: "en", notifications_email: true, compact_view: false };
  it("renders preferences", () => {
    const { container } = render(
      <UserPreferencesForm preferences={prefs} availableThemes={["light", "dark", "system"]}
        availableLanguages={["en", "es"]} onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Preferences");
    expect(container.textContent).toContain("Theme");
    expect(container.textContent).toContain("Language");
    expect(container.textContent).toContain("Email Notifications");
    expect(container.querySelectorAll("select").length).toBe(2);
  });
});
