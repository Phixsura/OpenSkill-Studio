import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-warmup-card";

describe("EndpointWarmupCard", () => {
  it("shows warmup progress", () => {
    const targets = [{ endpoint: "/users", method: "GET", completed: true, latency_ms: 50 }, { endpoint: "/orders", method: "GET", completed: false, latency_ms: 0 }];
    const { container } = render(<Card planId="p1" targets={targets} progressPct={50} isComplete={false} appName="App" />);
    expect(container.textContent).toContain("Endpoint Warmup");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("50ms");
  });
  it("shows complete", () => {
    const { container } = render(<Card planId="p1" targets={[]} progressPct={100} isComplete={true} appName="App" />);
    expect(container.textContent).toContain("Done");
  });
});
