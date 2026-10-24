import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UserPreferencesPage } from "@/components/user-preferences-page";

describe("UserPreferencesPage", () => {
  const prefs = {
    theme: { value: "dark", options: ["light", "dark", "system"], category: "appearance", is_default: false },
    language: { value: "en", options: ["en", "es"], category: "localization", is_default: true },
  };
  it("renders", () => {
    const { container } = render(
      <UserPreferencesPage preferences={prefs} categories={["appearance", "localization"]}
        onUpdate={vi.fn()} onReset={vi.fn()} />
    );
    expect(container.textContent).toContain("Preferences");
    expect(container.textContent).toContain("🎨");
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("Reset"); // dark is not default
    expect(container.textContent).toContain("🌐");
  });
});
