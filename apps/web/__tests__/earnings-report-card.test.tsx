import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EarningsReportCard } from "@/components/earnings-report-card";

describe("EarningsReportCard", () => {
  it("renders", () => {
    const { container } = render(
      <EarningsReportCard totalGross={4500} totalFees={1350} totalNet={3150}
        avgMonthlyNet={1050} bestMonth="2026-10" avgGrowthPct={40} />
    );
    expect(container.textContent).toContain("Earnings Report");
    expect(container.textContent).toContain("$3,150");
    expect(container.textContent).toContain("-$1,350");
    expect(container.textContent).toContain("+40%");
    expect(container.textContent).toContain("Best month: 2026-10");
  });
});
