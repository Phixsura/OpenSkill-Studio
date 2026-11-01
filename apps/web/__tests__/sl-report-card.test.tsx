import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlReportCard } from "@/components/sl-report-card";

describe("SlReportCard", () => {
  it("renders report", () => {
    const { container } = render(
      <SlReportCard grade="B" compliancePct={67} met={2} failed={1} period="monthly"
        slos={[
          { name: "Uptime", actual: 99.95, target: 99.9, met: true, budgetRemainingPct: 50 },
          { name: "Latency", actual: 99.0, target: 99.9, met: false, budgetRemainingPct: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Service Level Report");
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("Latency");
  });
});
