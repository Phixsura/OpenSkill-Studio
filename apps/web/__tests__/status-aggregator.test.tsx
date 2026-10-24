import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusAggregator } from "@/components/status-aggregator";

describe("StatusAggregator", () => {
  it("renders status", () => {
    const { container } = render(
      <StatusAggregator overallScore={97.5} status="operational"
        scores={{ services: 100, deploys: 98, errors: 99, latency: 100, incidents: 100 }} />
    );
    expect(container.textContent).toContain("97.5");
    expect(container.textContent).toContain("All Systems Operational");
    expect(container.textContent).toContain("services");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("deploys");
  });
});
