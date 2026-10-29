import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiQuotaAllocationCard from "../src/components/api-developer-api-api-quota-allocation-card";

const quotas = [
  { consumer_id: "acme", quota_type: "daily", allocated: 10000, used: 8500, remaining: 1500, usage_pct: 85, exhausted: false },
  { consumer_id: "beta", quota_type: "daily", allocated: 1000, used: 1000, remaining: 0, usage_pct: 100, exhausted: true },
];

describe("APIDeveloperAPIApiQuotaAllocationCard", () => {
  it("shows quotas", () => {
    const { container } = render(<APIDeveloperAPIApiQuotaAllocationCard quotas={quotas} exhaustedCount={1} appName="App" />);
    expect(container.textContent).toContain("Quota Allocation");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("8,500/10,000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiQuotaAllocationCard quotas={[]} exhaustedCount={0} appName="App" />);
    expect(container.textContent).toContain("No quotas");
  });
});
