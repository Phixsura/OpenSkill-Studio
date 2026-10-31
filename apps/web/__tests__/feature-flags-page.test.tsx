import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagsPage } from "@/components/feature-flags-page";

describe("FeatureFlagsPage", () => {
  const flags = [
    { key: "dark_mode", description: "Dark theme", enabled: true, rolloutPct: 100, environment: "all", createdBy: "Alice" },
    { key: "new_ui", description: "New interface", enabled: false, rolloutPct: 50, environment: "staging", createdBy: "Bob" },
  ];
  it("renders flags", () => {
    const { container } = render(
      <FeatureFlagsPage flags={flags} enabled={1} disabled={1} onToggle={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("new_ui");
    expect(container.textContent).toContain("1 on · 1 off");
    expect(container.textContent).toContain("+ New Flag");
  });
});
