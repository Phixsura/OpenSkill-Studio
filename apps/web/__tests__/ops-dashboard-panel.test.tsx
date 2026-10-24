import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpsDashboardPanel } from "@/components/ops-dashboard-panel";
describe("OpsDashboardPanel", () => {
  it("renders", () => {
    const { container } = render(
      <OpsDashboardPanel score={100} status="healthy" uptimePct={99.99} rps={5000}
        errorRatePct={0.1} p99Ms={100} activeIncidents={0} deploysToday={3} servicesCount={50} />
    );
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("Platform HEALTHY");
    expect(container.textContent).toContain("50 services");
    expect(container.textContent).toContain("5,000 rps");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("0.1%");
    expect(container.textContent).toContain("100ms");
  });
});
