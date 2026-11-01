import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AbTestDashboard } from "@/components/ab-test-dashboard";

describe("AbTestDashboard", () => {
  const variants = [
    { id: "v1", name: "Variant A", impressions: 1000, conversions: 50, conversion_rate: 5.0 },
    { id: "v2", name: "Variant B", impressions: 1000, conversions: 70, conversion_rate: 7.0 },
  ];
  it("renders", () => {
    const { container } = render(
      <AbTestDashboard experimentName="Title Test" variants={variants} winnerId="v2" />
    );
    expect(container.textContent).toContain("A/B Test: Title Test");
    expect(container.textContent).toContain("Variant A");
    expect(container.textContent).toContain("Variant B");
    expect(container.textContent).toContain("🏆 Winner");
    expect(container.textContent).toContain("7%");
  });
});
