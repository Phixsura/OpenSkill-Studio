import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConnectionPoolMonitor } from "@/components/connection-pool-monitor";

describe("ConnectionPoolMonitor", () => {
  const pools = [
    { name: "primary", active: 5, idle: 10, max_size: 20, utilization_pct: 25, healthy: true, waiting: 0 },
    { name: "replica", active: 18, idle: 2, max_size: 20, utilization_pct: 90, healthy: false, waiting: 3 },
  ];
  it("renders", () => {
    const { container } = render(<ConnectionPoolMonitor pools={pools} overallHealth="critical" />);
    expect(container.textContent).toContain("Connection Pools");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("primary");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("3 waiting");
  });
});
