import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-consumer-api-consumer-api-usage-quota-dashboard-card";

describe("UsageQuotaDashboardCard", () => {
  it("shows quotas", () => {
    const quotas = [{ name: "API Requests", used: 8000, limit: 10000, category: "requests" }, { name: "Webhooks", used: 9, limit: 10, category: "resources" }];
    const { container } = render(<Card quotas={quotas} overallPct={85} atRisk={1} exceeded={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Quota Dashboard");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("API Requests");
    expect(container.textContent).toContain("1 at risk");
  });
  it("shows empty", () => {
    const { container } = render(<Card quotas={[]} overallPct={0} atRisk={0} exceeded={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No quotas");
  });
});
