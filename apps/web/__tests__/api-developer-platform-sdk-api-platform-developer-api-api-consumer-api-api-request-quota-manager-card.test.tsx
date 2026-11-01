import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-quota-manager-card";

describe("RequestQuotaManagerCard", () => {
  it("shows quotas", () => {
    const quotas = [{ consumer_id: "c1", window_type: "hour", limit: 10000, used: 8500, remaining: 1500, usage_pct: 85, rollover: 0 }];
    const { container } = render(<Card quotas={quotas} nearLimitCount={1} appName="App" />);
    expect(container.textContent).toContain("Quota Manager");
    expect(container.textContent).toContain("1 near limit");
    expect(container.textContent).toContain("8,500/10,000");
  });
  it("shows empty", () => {
    const { container } = render(<Card quotas={[]} nearLimitCount={0} appName="App" />);
    expect(container.textContent).toContain("No quotas");
  });
});
