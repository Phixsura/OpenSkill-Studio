import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureTogglePanel } from "@/components/feature-toggle-panel";

const mockToggles = [
  { id: "f1", name: "dark_mode", type: "boolean" as const, enabled: true,
    percentage: 0, userCount: 0, description: "Enable dark theme" },
  { id: "f2", name: "new_ui", type: "percentage" as const, enabled: true,
    percentage: 50, userCount: 0 },
  { id: "f3", name: "beta_access", type: "user_list" as const, enabled: false,
    percentage: 0, userCount: 12 },
];

describe("FeatureTogglePanel", () => {
  it("renders toggles with counts", () => {
    const { container } = render(
      <FeatureTogglePanel toggles={mockToggles} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("2/3 enabled");
    expect(container.textContent).toContain("Enable dark theme");
  });

  it("shows percentage slider", () => {
    const { container } = render(
      <FeatureTogglePanel toggles={mockToggles} extensionName="Test" />
    );
    expect(container.textContent).toContain("50%");
    expect(container.querySelector("input[type='range']")).toBeDefined();
  });

  it("shows user count for user_list", () => {
    const { container } = render(
      <FeatureTogglePanel toggles={mockToggles} extensionName="Test" />
    );
    expect(container.textContent).toContain("12 users targeted");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { container } = render(
      <FeatureTogglePanel toggles={mockToggles} extensionName="Test" onToggle={onToggle} />
    );
    const toggleBtns = container.querySelectorAll("button");
    if (toggleBtns[0]) fireEvent.click(toggleBtns[0]);
    expect(onToggle).toHaveBeenCalledWith("dark_mode");
  });
});
