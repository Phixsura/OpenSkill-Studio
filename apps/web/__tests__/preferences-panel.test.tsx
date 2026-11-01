import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PreferencesPanel } from "@/components/preferences-panel";

describe("PreferencesPanel", () => {
  const settings = [
    { key: "theme", label: "Theme", type: "select", options: ["system", "light", "dark"] },
    { key: "previews", label: "Previews", type: "boolean" },
  ];
  it("renders settings", () => {
    const { container } = render(
      <PreferencesPanel settings={settings} values={{ theme: "dark", previews: true }} onChange={vi.fn()} onReset={vi.fn()} />
    );
    expect(container.textContent).toContain("Theme");
    expect(container.textContent).toContain("Previews");
  });
  it("reset button", () => {
    const fn = vi.fn();
    const { container } = render(
      <PreferencesPanel settings={settings} values={{}} onChange={vi.fn()} onReset={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Reset"))!);
    expect(fn).toHaveBeenCalled();
  });
});
