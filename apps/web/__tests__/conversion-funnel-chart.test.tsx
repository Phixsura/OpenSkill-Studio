import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConversionFunnelChart } from "@/components/conversion-funnel-chart";

describe("ConversionFunnelChart", () => {
  const steps = [
    { name: "Visit", count: 10000, pct_of_total: 100, drop_off: 0, drop_off_pct: 0 },
    { name: "Details", count: 4000, pct_of_total: 40, drop_off: 6000, drop_off_pct: 60 },
    { name: "Install", count: 1200, pct_of_total: 12, drop_off: 2800, drop_off_pct: 70 },
  ];
  it("renders", () => {
    const { container } = render(
      <ConversionFunnelChart steps={steps} overallConversion={12} worstStep="Install" />
    );
    expect(container.textContent).toContain("Conversion Funnel");
    expect(container.textContent).toContain("12% conversion");
    expect(container.textContent).toContain("Visit");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("↓ 60%");
    expect(container.textContent).toContain("Biggest drop: Install");
  });
});
