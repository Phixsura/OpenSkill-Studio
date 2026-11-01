import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-service-mesh-topology-card";

describe("ServiceMeshCard", () => {
  it("shows topology", () => {
    const nodes = [{ service_id: "api", name: "API Gateway", healthy: true, request_rate: 150 }];
    const edges = [{ source: "api", target: "db", protocol: "http", avg_latency_ms: 5 }];
    const { container } = render(<Card nodes={nodes} edges={edges} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("Service Mesh");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("150 req/s");
  });
  it("shows unhealthy", () => {
    const { container } = render(<Card nodes={[]} edges={[]} unhealthyCount={2} appName="App" />);
    expect(container.textContent).toContain("2 down");
  });
});
