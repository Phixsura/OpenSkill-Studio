import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConversionFunnelChart } from "@/components/conversion-funnel-chart";

describe("ConversionFunnelChart", () => {
  const steps = [
    { step: "Visit", count: 10000, dropOffPct: 0, conversionPct: 100, icon: "👁️" },
    { step: "Install", count: 600, dropOffPct: 94, conversionPct: 6, icon: "✅" },
  ];
  it("renders funnel", () => {
    const { container } = render(
      <ConversionFunnelChart steps={steps} overallConversion={6} worstStep="Install" />
    );
    expect(container.textContent).toContain("Conversion Funnel");
    expect(container.textContent).toContain("Visit");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("6%");
    expect(container.textContent).toContain("Biggest drop-off: Install");
  });
});
