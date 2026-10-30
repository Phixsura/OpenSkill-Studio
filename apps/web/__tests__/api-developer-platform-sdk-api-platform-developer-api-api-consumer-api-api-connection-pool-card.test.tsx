import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-connection-pool-card";

describe("ConnectionPoolCard", () => {
  it("shows pools", () => {
    const pools = [{ consumer_id: "c1", max_connections: 100, active: 50, idle: 10, utilization_pct: 50, reuse_rate: 75 }];
    const { container } = render(<Card pools={pools} appName="App" />);
    expect(container.textContent).toContain("Connection Pools");
    expect(container.textContent).toContain("50/100");
    expect(container.textContent).toContain("75% reuse");
  });
  it("shows empty", () => {
    const { container } = render(<Card pools={[]} appName="App" />);
    expect(container.textContent).toContain("No connection pools");
  });
});
