import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-api-consumer-api-api-consumer-api-api-consumer-api-quota-usage-summary-card";

describe("QuotaUsageSummaryCard", () => {
  it("shows quotas", () => {
    const quotas = [{ resource: "api_keys", used: 8, limit: 10, usagePct: 80, status: "warning" }];
    const { container } = render(<Card quotas={quotas} overallStatus="warning" atRiskCount={1} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Quota Summary");
    expect(container.textContent).toContain("api_keys");
    expect(container.textContent).toContain("8/10");
    expect(container.textContent).toContain("1 at risk");
  });
  it("shows all ok", () => {
    const quotas = [{ resource: "webhooks", used: 2, limit: 10, usagePct: 20, status: "ok" }];
    const { container } = render(<Card quotas={quotas} overallStatus="ok" atRiskCount={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("All OK");
  });
});
