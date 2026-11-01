import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-cost-estimator-card";

describe("CostEstimatorCard", () => {
  it("shows estimates", () => {
    const estimates = [{ tier: "Free", total_dollars: "$100.00", base_dollars: "$0.00", per_request: "0.05¢" }, { tier: "Pro", total_dollars: "$69.99", base_dollars: "$49.99", per_request: "0.01¢" }];
    const { container } = render(<Card estimates={estimates} requestCount={200000} appName="App" />);
    expect(container.textContent).toContain("Cost Estimator");
    expect(container.textContent).toContain("200,000");
    expect(container.textContent).toContain("$69.99");
  });
  it("shows empty", () => {
    const { container } = render(<Card estimates={[]} requestCount={0} appName="App" />);
    expect(container.textContent).toContain("No pricing data");
  });
});
