import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagToggleList } from "@/components/feature-flag-toggle-list";

describe("FeatureFlagToggleList", () => {
  const flags = [
    { name: "dark_mode", description: "Dark mode", enabled: true, rollout: 100 },
    { name: "beta_ai", description: "AI features", enabled: false, rollout: 0 },
  ];
  it("renders flags", () => {
    const { container } = render(<FeatureFlagToggleList flags={flags} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("Off");
  });
  it("toggle", () => {
    const fn = vi.fn();
    const { container } = render(<FeatureFlagToggleList flags={flags} onToggle={fn} />);
    const toggles = container.querySelectorAll("button");
    fireEvent.click(toggles[0]);
    expect(fn).toHaveBeenCalledWith("dark_mode", false);
  });
});
