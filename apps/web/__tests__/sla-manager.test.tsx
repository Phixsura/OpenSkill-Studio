import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaManager } from "@/components/sla-manager";

describe("SlaManager", () => {
  it("renders", () => {
    const { container } = render(
      <SlaManager service="api" compliancePct={100} fullyCompliant={true}
        results={[
          { metric: "uptime_pct", target: 99.9, actual: 99.95, met: true },
          { metric: "p99_ms", target: 500, actual: 300, met: true },
        ]} />
    );
    expect(container.textContent).toContain("SLA: api");
    expect(container.textContent).toContain("Compliant");
    expect(container.textContent).toContain("uptime_pct");
    expect(container.textContent).toContain("99.95");
  });
});
