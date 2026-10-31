import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-api-consumer-api-request-flow-analyzer-card";

describe("RequestFlowAnalyzerCard", () => {
  it("shows analysis", () => {
    const analysis = { totalFlows: 100, avgMs: 150, bottleneckService: "db", bottleneckMs: 80, slowestStep: "Query", errors: 5 };
    const flows = [{ id: "f1", endpoint: "/api/orders", totalMs: 150, steps: [{ name: "Auth", service: "auth", latencyMs: 20, status: "ok" }, { name: "Query", service: "db", latencyMs: 100, status: "slow" }] }];
    const { container } = render(<Card analysis={analysis} recentFlows={flows} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Request Flow Analyzer");
    expect(container.textContent).toContain("150ms");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("/api/orders");
  });
  it("shows empty", () => {
    const analysis = { totalFlows: 0, avgMs: 0, bottleneckService: "", bottleneckMs: 0, slowestStep: "", errors: 0 };
    const { container } = render(<Card analysis={analysis} recentFlows={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("0 flows");
  });
});
