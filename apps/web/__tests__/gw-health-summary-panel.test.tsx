import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwHealthSummaryPanel } from "@/components/gw-health-summary-panel";
describe("GwHealthSummaryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwHealthSummaryPanel score={100} status="healthy" rps={5000}
        errorRatePct={0.1} p99Ms={100} uptimePct={99.99} connUtilPct={10} />
    );
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("Gateway HEALTHY");
    expect(container.textContent).toContain("5,000 rps");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("0.1%");
    expect(container.textContent).toContain("100ms");
  });
});
