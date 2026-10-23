import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConnectionPoolMonitor } from "@/components/connection-pool-monitor";

describe("ConnectionPoolMonitor", () => {
  it("renders pools", () => {
    const { container } = render(
      <ConnectionPoolMonitor pools={[
        { name: "Primary DB", stats: { maxSize: 20, active: 15, idle: 5, utilizationDisplay: "75.0%", waits: 2, health: "busy" } },
        { name: "Read Replica", stats: { maxSize: 10, active: 3, idle: 7, utilizationDisplay: "30.0%", waits: 0, health: "healthy" } },
      ]} />
    );
    expect(container.textContent).toContain("Connection Pools");
    expect(container.textContent).toContain("Primary DB");
    expect(container.textContent).toContain("75.0%");
    expect(container.textContent).toContain("busy");
    expect(container.textContent).toContain("2 waits");
    expect(container.textContent).toContain("Read Replica");
    expect(container.textContent).toContain("healthy");
  });
});
