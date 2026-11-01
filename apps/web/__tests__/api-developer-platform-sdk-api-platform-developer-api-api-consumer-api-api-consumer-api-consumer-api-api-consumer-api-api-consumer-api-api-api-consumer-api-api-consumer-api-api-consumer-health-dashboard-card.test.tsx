import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-api-consumer-api-api-consumer-health-dashboard-card";

describe("ConsumerHealthDashboardCard", () => {
  it("shows dashboard", () => {
    const indicators = [{ name: "Error Rate", status: "healthy", value: 0.1, threshold: 1, unit: "%" }];
    const { container } = render(<Card consumerId="c1" overallStatus="healthy" healthScore={100} indicators={indicators} activeAlerts={0} activeIncidents={0} appName="App" />);
    expect(container.textContent).toContain("Health Dashboard");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("Error Rate");
  });
  it("shows alerts", () => {
    const { container } = render(<Card consumerId="c1" overallStatus="critical" healthScore={0} indicators={[]} activeAlerts={3} activeIncidents={1} appName="App" />);
    expect(container.textContent).toContain("3 alerts");
    expect(container.textContent).toContain("1 incidents");
  });
});
