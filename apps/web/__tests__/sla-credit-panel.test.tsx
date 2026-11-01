import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaCreditPanel } from "@/components/sla-credit-panel";
describe("SlaCreditPanel", () => {
  it("renders breach", () => {
    const { container } = render(
      <SlaCreditPanel slaMet={false} creditPct={10} creditAmount={1000}
        uptimePct={99.5} gap={0.4} monthlyRevenue={10000} />
    );
    expect(container.textContent).toContain("SLA Breach");
    expect(container.textContent).toContain("10% Credit");
    expect(container.textContent).toContain("0.4% gap");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("$1,000");
    expect(container.textContent).toContain("$10,000");
  });
  it("renders met", () => {
    const { container } = render(
      <SlaCreditPanel slaMet={true} creditPct={0} creditAmount={0}
        uptimePct={99.99} gap={0} monthlyRevenue={10000} />
    );
    expect(container.textContent).toContain("SLA Met");
    expect(container.textContent).toContain("No Credits Owed");
  });
});
