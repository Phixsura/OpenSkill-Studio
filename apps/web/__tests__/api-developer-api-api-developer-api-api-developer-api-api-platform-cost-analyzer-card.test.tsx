import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzerCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-platform-cost-analyzer-card";

const items = [
  { dimension: "compute", cost_cents: 50000, usage: 100, unit: "cpu-hours" },
  { dimension: "api_calls", cost_cents: 30000, usage: 1000000, unit: "requests" },
];

describe("Card", () => {
  it("shows costs", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzerCard period="2025-01" items={items} totalCents={80000} totalSpendCents={200000} appName="App" />);
    expect(container.textContent).toContain("Cost Analyzer");
    expect(container.textContent).toContain("$800.00");
    expect(container.textContent).toContain("$2000.00");
    expect(container.textContent).toContain("compute");
    expect(container.textContent).toContain("1,000,000 requests");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzerCard period="2025-01" items={[]} totalCents={0} totalSpendCents={0} appName="App" />);
    expect(container.textContent).toContain("No cost data");
  });
});
