import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagsPanel } from "@/components/feature-flags-panel";

describe("FeatureFlagsPanel", () => {
  it("renders flags", () => {
    const flags = [{ key: "dark_mode", description: "Dark mode", enabled: true, rollout_pct: 100 }];
    const { container } = render(<FeatureFlagsPanel flags={flags} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("100% rollout");
  });
  it("empty state", () => {
    const { container } = render(<FeatureFlagsPanel flags={[]} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("No feature flags");
  });
  it("toggles", () => {
    const fn = vi.fn();
    const flags = [{ key: "x", description: "X", enabled: false, rollout_pct: 50 }];
    const { container } = render(<FeatureFlagsPanel flags={flags} onToggle={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("x", true);
  });
});
