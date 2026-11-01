import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-platform-health-aggregator-card";

describe("PlatformHealthAggregatorCard", () => {
  it("shows health", () => {
    const worst = [{ id: "c2", healthScore: 30, errorRate: 10, avgMs: 500, status: "critical" }];
    const { container } = render(<Card totalConsumers={10} healthy={8} degraded={1} critical={1} avgScore={85} overall="critical" topIssues={["1 consumers with >5% error rate"]} worstConsumers={worst} appName="App" />);
    expect(container.textContent).toContain("Platform Health");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("c2");
    expect(container.textContent).toContain(">5% error rate");
  });
  it("shows all healthy", () => {
    const { container } = render(<Card totalConsumers={5} healthy={5} degraded={0} critical={0} avgScore={95} overall="healthy" topIssues={[]} worstConsumers={[]} appName="App" />);
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("95%");
  });
});
