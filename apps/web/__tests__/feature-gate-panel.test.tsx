import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureGatePanel } from "@/components/feature-gate-panel";

describe("FeatureGatePanel", () => {
  const features = [
    { feature: "max_apps", type: "limit", value: 5, display: "5" },
    { feature: "analytics", type: "boolean", value: false, display: "✗" },
    { feature: "custom_domain", type: "boolean", value: true, display: "✓" },
  ];
  it("renders plan features", () => {
    const { container } = render(<FeatureGatePanel plan="free" features={features} onUpgrade={vi.fn()} />);
    expect(container.textContent).toContain("free");
    expect(container.textContent).toContain("max apps");
    expect(container.textContent).toContain("analytics");
    expect(container.textContent).toContain("Upgrade");
  });
});
