import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConnectionPoolMonitor } from "@/components/connection-pool-monitor";

describe("ConnectionPoolMonitor", () => {
  it("renders pool stats", () => {
    const { container } = render(
      <ConnectionPoolMonitor stats={{ active: 5, idle: 3, waiting: 0, maxSize: 20, utilizationPct: 25, healthy: true }} />
    );
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("Healthy");
    expect(container.textContent).toContain("25%");
  });
});
