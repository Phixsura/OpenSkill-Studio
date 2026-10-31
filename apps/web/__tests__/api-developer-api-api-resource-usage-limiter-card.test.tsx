import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiResourceUsageLimiterCard from "../src/components/api-developer-api-api-resource-usage-limiter-card";

const limits = [
  { resource_type: "compute", limit: 100, used: 75, remaining: 25, usage_pct: 75, exceeded: false, unit: "cpu-hours" },
  { resource_type: "storage", limit: 10, used: 10, remaining: 0, usage_pct: 100, exceeded: true, unit: "GB" },
];

describe("APIDeveloperAPIApiResourceUsageLimiterCard", () => {
  it("shows resource limits", () => {
    const { container } = render(<APIDeveloperAPIApiResourceUsageLimiterCard limits={limits} exceededCount={1} appName="App" />);
    expect(container.textContent).toContain("Resource Limits");
    expect(container.textContent).toContain("1 exceeded");
    expect(container.textContent).toContain("compute");
    expect(container.textContent).toContain("75/100 cpu-hours");
    expect(container.textContent).toContain("10/10 GB");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiResourceUsageLimiterCard limits={[]} exceededCount={0} appName="App" />);
    expect(container.textContent).toContain("No resource limits");
  });
});
