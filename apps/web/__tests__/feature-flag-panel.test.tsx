import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagPanel } from "@/components/feature-flag-panel";

const flags = [
  { flagId: "dark", name: "Dark Mode", description: "Enable dark theme", enabled: true, rolloutPct: 50 },
  { flagId: "beta", name: "Beta UI", description: "", enabled: false, rolloutPct: 0 },
];

describe("FeatureFlagPanel", () => {
  it("renders flags", () => {
    const { container } = render(<FeatureFlagPanel flags={flags} />);
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Beta UI");
  });
  it("toggle flag", () => {
    const fn = vi.fn();
    const { container } = render(<FeatureFlagPanel flags={flags} onToggle={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]); // Disable dark mode
    expect(fn).toHaveBeenCalledWith("dark", false);
  });
});
