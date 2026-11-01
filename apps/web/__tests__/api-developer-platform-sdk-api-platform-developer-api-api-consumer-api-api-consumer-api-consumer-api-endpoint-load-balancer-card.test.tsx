import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-endpoint-load-balancer-card";

describe("EndpointLoadBalancerCard", () => {
  it("shows instances", () => {
    const instances = [{ id: "i1", host: "10.0.0.1", port: 8080, healthy: true, connections: 5, weight: 2 }];
    const { container } = render(<Card instances={instances} endpointPath="/api" strategy="round_robin" appName="App" />);
    expect(container.textContent).toContain("Load Balancer");
    expect(container.textContent).toContain("10.0.0.1:8080");
    expect(container.textContent).toContain("5 conn");
    expect(container.textContent).toContain("round robin");
  });
  it("shows empty", () => {
    const { container } = render(<Card instances={[]} endpointPath="/api" strategy="least_connections" appName="App" />);
    expect(container.textContent).toContain("No backend instances");
  });
});
