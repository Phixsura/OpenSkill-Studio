import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiABTestManagerCard from "../src/components/api-developer-api-api-ab-test-manager-card";

const tests = [{
  test_id: "t1", endpoint: "/api/checkout", status: "completed", winner: "variant_a",
  variants: [
    { name: "control", weight: 50, impressions: 500, conversions: 25, conversion_rate: 5 },
    { name: "variant_a", weight: 50, impressions: 500, conversions: 40, conversion_rate: 8 },
  ],
}];

describe("APIDeveloperAPIApiABTestManagerCard", () => {
  it("shows A/B tests", () => {
    const { container } = render(<APIDeveloperAPIApiABTestManagerCard tests={tests} appName="App" />);
    expect(container.textContent).toContain("A/B Tests");
    expect(container.textContent).toContain("/api/checkout");
    expect(container.textContent).toContain("control (50%)");
    expect(container.textContent).toContain("8% CVR");
    expect(container.textContent).toContain("completed");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiABTestManagerCard tests={[]} appName="App" />);
    expect(container.textContent).toContain("No A/B tests");
  });
});
