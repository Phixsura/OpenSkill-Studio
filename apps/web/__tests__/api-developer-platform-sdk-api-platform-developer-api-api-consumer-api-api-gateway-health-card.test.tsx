import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-gateway-health-card";

describe("GatewayHealthCard", () => {
  it("shows nodes", () => {
    const nodes = [{ node_id: "n1", region: "us-east", healthy: true, rps: 100, error_rate: 0.5 }];
    const { container } = render(<Card nodes={nodes} unhealthyCount={0} totalRps={100} appName="App" />);
    expect(container.textContent).toContain("Gateway Health");
    expect(container.textContent).toContain("us-east");
    expect(container.textContent).toContain("100 rps total");
  });
  it("shows unhealthy", () => {
    const { container } = render(<Card nodes={[]} unhealthyCount={2} totalRps={0} appName="App" />);
    expect(container.textContent).toContain("2 down");
  });
});
