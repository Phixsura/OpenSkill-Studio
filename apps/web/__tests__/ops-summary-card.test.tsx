import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpsSummaryCard } from "@/components/ops-summary-card";

describe("OpsSummaryCard", () => {
  it("renders summary", () => {
    const { container } = render(
      <OpsSummaryCard uptimePct={99.99} deploysToday={5} openIncidents={0}
        errorRate={0.1} changes24h={12} riskLevel="low" status="nominal" />
    );
    expect(container.textContent).toContain("Ops Summary");
    expect(container.textContent).toContain("nominal");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("0.1%");
    expect(container.textContent).toContain("12");
  });
});
