import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-platform-summary-dashboard-card";

describe("PlatformSummaryDashboardCard", () => {
  it("shows summary", () => {
    const metrics = [{ name: "Revenue", value: 25000, unit: "USD", trend: "up" }];
    const { container } = render(<Card totalConsumers={50} activeConsumers={45} totalKeys={120} requestsToday={500000} avgLatencyMs={75} errorRatePct={0.2} uptimePct={99.99} healthScore={95} metrics={metrics} activeIncidents={0} appName="App" />);
    expect(container.textContent).toContain("Platform Summary");
    expect(container.textContent).toContain("45/50");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("Revenue");
  });
  it("shows incidents", () => {
    const { container } = render(<Card totalConsumers={10} activeConsumers={8} totalKeys={20} requestsToday={1000} avgLatencyMs={100} errorRatePct={5} uptimePct={98} healthScore={60} metrics={[]} activeIncidents={2} appName="App" />);
    expect(container.textContent).toContain("2 active incidents");
  });
});
