import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-quota-allocation-card";

describe("QuotaAllocationCard", () => {
  it("shows quotas", () => {
    const quotas = [{ consumer_id: "c1", resource: "requests", limit: 10000, used: 8500, usage_pct: 85 }];
    const { container } = render(<Card quotas={quotas} nearLimitCount={1} appName="App" />);
    expect(container.textContent).toContain("Quota Allocation");
    expect(container.textContent).toContain("1 near limit");
    expect(container.textContent).toContain("c1 / requests");
    expect(container.textContent).toContain("8,500 / 10,000");
  });
  it("shows empty", () => {
    const { container } = render(<Card quotas={[]} nearLimitCount={0} appName="App" />);
    expect(container.textContent).toContain("No quotas allocated");
  });
});
