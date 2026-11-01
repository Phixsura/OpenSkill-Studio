import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-cost-tracker-card";

describe("EndpointCostTrackerCard", () => {
  it("shows costs", () => {
    const costs = [{ endpoint: "/users", method: "GET", total_cost_dollars: "$10.00", total_requests: 100000, cost_per_request: 0.01 }];
    const { container } = render(<Card costs={costs} totalCostDollars="$10.00" appName="App" />);
    expect(container.textContent).toContain("Endpoint Costs");
    expect(container.textContent).toContain("$10.00");
    expect(container.textContent).toContain("100,000 reqs");
  });
  it("shows empty", () => {
    const { container } = render(<Card costs={[]} totalCostDollars="$0.00" appName="App" />);
    expect(container.textContent).toContain("No cost data");
  });
});
