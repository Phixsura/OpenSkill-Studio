import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-capacity-card";

describe("EndpointCapacityCard", () => {
  it("shows capacities", () => {
    const caps = [{ endpoint: "/api", method: "GET", max_rps: 100, current_rps: 85, utilization_pct: 85, status: "high" }];
    const { container } = render(<Card capacities={caps} saturatedCount={0} appName="App" />);
    expect(container.textContent).toContain("Endpoint Capacity");
    expect(container.textContent).toContain("85/100 rps");
  });
  it("shows saturated alert", () => {
    const { container } = render(<Card capacities={[]} saturatedCount={2} appName="App" />);
    expect(container.textContent).toContain("2 saturated");
  });
});
