import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlannerCard from "../src/components/api-developer-api-api-developer-api-api-platform-capacity-planner-card";

const plans = [
  { resource: "api_capacity", current_usage: 75000, max_capacity: 100000, utilization_pct: 75, months_until_full: 2.5, needs_scaling: true, unit: "rps", growth_rate_pct: 10 },
  { resource: "storage", current_usage: 200, max_capacity: 1000, utilization_pct: 20, months_until_full: 40, needs_scaling: false, unit: "GB", growth_rate_pct: 5 },
];

describe("Card", () => {
  it("shows capacity plans", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlannerCard plans={plans} scalingNeeded={1} appName="App" />);
    expect(container.textContent).toContain("Capacity Planner");
    expect(container.textContent).toContain("1 need scaling");
    expect(container.textContent).toContain("api_capacity");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("2.5mo left");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlannerCard plans={[]} scalingNeeded={0} appName="App" />);
    expect(container.textContent).toContain("No capacity plans");
  });
});
