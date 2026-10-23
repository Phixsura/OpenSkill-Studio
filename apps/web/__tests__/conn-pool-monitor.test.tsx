import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConnPoolMonitor } from "@/components/conn-pool-monitor";

describe("ConnPoolMonitor", () => {
  it("renders pools", () => {
    const { container } = render(
      <ConnPoolMonitor pools={[
        { name: "primary", active: 8, idle: 12, total: 20, maxSize: 20, utilization: 40, health: "healthy", waiting: 0 },
        { name: "replica", active: 18, idle: 2, total: 20, maxSize: 20, utilization: 90, health: "saturated", waiting: 3 },
      ]} />
    );
    expect(container.textContent).toContain("Connection Pools");
    expect(container.textContent).toContain("primary");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("replica");
    expect(container.textContent).toContain("saturated");
    expect(container.textContent).toContain("3 waiting");
  });
});
