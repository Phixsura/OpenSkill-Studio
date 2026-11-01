import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-api-consumer-api-consumer-api-api-request-correlation-card";

describe("RequestCorrelationCard", () => {
  it("shows chain", () => {
    const requests = [
      { correlationId: "root", method: "GET", path: "/api/orders", status: 200, latencyMs: 80, service: "gateway", isChild: false },
      { correlationId: "child", method: "GET", path: "/api/users/1", status: 200, latencyMs: 30, service: "user-svc", isChild: true },
    ];
    const { container } = render(<Card requests={requests} rootId="root" totalLatencyMs={110} serviceCount={2} appName="App" />);
    expect(container.textContent).toContain("Request Correlation");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("2 services");
  });
  it("shows empty", () => {
    const { container } = render(<Card requests={[]} rootId="" totalLatencyMs={0} serviceCount={0} appName="App" />);
    expect(container.textContent).toContain("No correlated requests");
  });
});
