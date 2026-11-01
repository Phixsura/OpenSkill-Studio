import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiCostEstimatorCard from "../src/components/api-developer-api-api-cost-estimator-card";

const estimates = [
  { tier: "free", api_cost: 0, webhook_cost: 0, storage_cost: 0, total_cost: 0 },
  { tier: "pro", api_cost: 30, webhook_cost: 25, storage_cost: 0.5, total_cost: 55.5 },
];

describe("APIDeveloperAPIApiCostEstimatorCard", () => {
  it("shows cost estimates", () => {
    const { container } = render(<APIDeveloperAPIApiCostEstimatorCard estimates={estimates} recommendedTier="pro" appName="App" />);
    expect(container.textContent).toContain("Cost Estimator");
    expect(container.textContent).toContain("recommended: pro");
    expect(container.textContent).toContain("$0.00/mo");
    expect(container.textContent).toContain("$55.50/mo");
  });
});
