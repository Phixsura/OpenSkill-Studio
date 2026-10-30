import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-load-balancer-card";

describe("LoadBalancerCard", () => {
  it("shows instances", () => {
    const instances = [{ instance_id: "i1", host: "host1:8080", healthy: true, active_connections: 15 }];
    const { container } = render(<Card strategy="round_robin" instances={instances} healthyCount={1} appName="App" />);
    expect(container.textContent).toContain("Load Balancer");
    expect(container.textContent).toContain("round_robin");
    expect(container.textContent).toContain("host1:8080");
    expect(container.textContent).toContain("15 conn");
  });
  it("shows healthy count", () => {
    const { container } = render(<Card strategy="least_connections" instances={[]} healthyCount={0} appName="App" />);
    expect(container.textContent).toContain("0/0 healthy");
  });
});
