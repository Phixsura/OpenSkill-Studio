import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-circuit-monitor-card";

describe("CircuitMonitorCard", () => {
  it("shows circuits", () => {
    const circuits = [{ endpoint: "/users", state: "closed", failure_count: 0 }, { endpoint: "/orders", state: "open", failure_count: 5 }];
    const summary = { total_circuits: 2, closed_count: 1, open_count: 1, half_open_count: 0 };
    const { container } = render(<Card circuits={circuits} summary={summary} appName="App" />);
    expect(container.textContent).toContain("Circuit Monitor");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("/orders");
  });
  it("shows empty", () => {
    const summary = { total_circuits: 0, closed_count: 0, open_count: 0, half_open_count: 0 };
    const { container } = render(<Card circuits={[]} summary={summary} appName="App" />);
    expect(container.textContent).toContain("No circuits");
  });
});
