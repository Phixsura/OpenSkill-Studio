import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookConnectionPoolCard from "../src/components/api-developer-api-api-webhook-connection-pool-card";

const pools = [
  { destination: "https://api.example.com", max_connections: 100, active_connections: 75, idle_connections: 25, utilization_pct: 75, healthy: true, total_requests_served: 50000 },
  { destination: "https://slow.example.com", max_connections: 10, active_connections: 9, idle_connections: 1, utilization_pct: 90, healthy: false, total_requests_served: 1000 },
];

describe("APIDeveloperAPIApiWebhookConnectionPoolCard", () => {
  it("shows pools", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookConnectionPoolCard pools={pools} totalActive={84} unhealthyCount={1} appName="App" />);
    expect(container.textContent).toContain("Connection Pools");
    expect(container.textContent).toContain("84 active");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("90%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookConnectionPoolCard pools={[]} totalActive={0} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("No connection pools");
  });
});
