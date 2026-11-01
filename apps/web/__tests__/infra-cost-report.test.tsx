import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InfraCostReport } from "@/components/infra-cost-report";

describe("InfraCostReport", () => {
  it("renders report", () => {
    const { container } = render(
      <InfraCostReport displayTotal="$7,000.00" forecastTotal={7440} topCategory="compute"
        items={[
          { category: "compute", amount: 5000, changePct: 10, forecast: 5500 },
          { category: "storage", amount: 1200, changePct: -5, forecast: 1140 },
        ]} />
    );
    expect(container.textContent).toContain("Infrastructure Costs");
    expect(container.textContent).toContain("$7,000.00");
    expect(container.textContent).toContain("7,440");
    expect(container.textContent).toContain("compute");
    expect(container.textContent).toContain("$5,000");
    expect(container.textContent).toContain("10%");
  });
});
