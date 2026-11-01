import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureGatePanel } from "@/components/feature-gate-panel";

const mockGates = [
  { feature: "network_access", minTier: "starter", enabled: true, description: "Outbound HTTP",
    isAvailable: true, reason: "tier pro >= starter", hasOverride: false },
  { feature: "gpu_compute", minTier: "enterprise", enabled: true, description: "GPU acceleration",
    isAvailable: false, reason: "Requires enterprise", hasOverride: false },
  { feature: "premium_api", minTier: "enterprise", enabled: true, description: "Premium APIs",
    isAvailable: true, reason: "admin override", hasOverride: true },
];

describe("FeatureGatePanel", () => {
  it("renders gates with tier", () => {
    const { container } = render(
      <FeatureGatePanel gates={mockGates} currentTier="pro" />
    );
    expect(container.textContent).toContain("network_access");
    expect(container.textContent).toContain("starter+");
    expect(container.textContent).toContain("2/3 available");
  });

  it("shows locked features", () => {
    const { container } = render(
      <FeatureGatePanel gates={mockGates} currentTier="pro" />
    );
    expect(container.textContent).toContain("🔒");
    expect(container.textContent).toContain("enterprise+");
  });

  it("shows override indicator", () => {
    const { container } = render(
      <FeatureGatePanel gates={mockGates} currentTier="pro" />
    );
    expect(container.textContent).toContain("override");
  });

  it("calls onOverride for locked features", () => {
    const onOverride = vi.fn();
    const { getByText } = render(
      <FeatureGatePanel gates={mockGates} currentTier="pro" onOverride={onOverride} />
    );
    fireEvent.click(getByText("Override"));
    expect(onOverride).toHaveBeenCalledWith("gpu_compute", true);
  });
});
