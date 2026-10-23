import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagPanel } from "@/components/feature-flag-panel";

describe("FeatureFlagPanel", () => {
  const flags = [
    { key: "dark_mode", enabled: true, percentage: 100, description: "Dark mode toggle" },
    { key: "new_ui", enabled: false, percentage: 50, description: "New UI experiment" },
  ];
  it("renders flags", () => {
    const { container } = render(<FeatureFlagPanel flags={flags} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("new_ui");
    expect(container.textContent).toContain("1/2 active");
  });
  it("toggle calls handler", () => {
    const fn = vi.fn();
    const { container } = render(<FeatureFlagPanel flags={flags} onToggle={fn} />);
    const buttons = container.querySelectorAll("button");
    fireEvent.click(buttons[0]);
    expect(fn).toHaveBeenCalledWith("dark_mode");
  });
});
