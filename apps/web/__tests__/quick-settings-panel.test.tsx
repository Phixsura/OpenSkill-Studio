import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickSettingsPanel } from "@/components/quick-settings-panel";

describe("QuickSettingsPanel", () => {
  const settings = {
    dark_mode: { value: "dark", type: "select", label: "Theme", category: "appearance",
      modified: true, options: ["light", "dark", "system"] },
    notifications: { value: true, type: "boolean", label: "Push notifications",
      category: "general", modified: false },
  };
  it("renders", () => {
    const { container } = render(
      <QuickSettingsPanel settings={settings} categories={["appearance", "general"]}
        modifiedCount={1} onToggle={vi.fn()} onReset={vi.fn()} />
    );
    expect(container.textContent).toContain("Quick Settings");
    expect(container.textContent).toContain("1 modified");
    expect(container.textContent).toContain("Theme");
    expect(container.textContent).toContain("Push notifications");
    expect(container.textContent).toContain("Reset");
    expect(container.textContent).toContain("🎨");
  });
});
