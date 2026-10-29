import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiHealthDashboardCard from "../src/components/api-developer-api-api-developer-api-api-health-dashboard-card";

const services = [
  { service_name: "API Gateway", status: "healthy", response_time_ms: 15, consecutive_failures: 0, error_message: "" },
  { service_name: "Database", status: "degraded", response_time_ms: 500, consecutive_failures: 3, error_message: "Slow queries" },
];

describe("APIDeveloperAPIApiDeveloperApiApiHealthDashboardCard", () => {
  it("shows health dashboard", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiHealthDashboardCard services={services} overallStatus="degraded" appName="App" />);
    expect(container.textContent).toContain("Health Dashboard");
    expect(container.textContent).toContain("DEGRADED");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("15ms");
    expect(container.textContent).toContain("3 fails");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiHealthDashboardCard services={[]} overallStatus="unknown" appName="App" />);
    expect(container.textContent).toContain("No services");
  });
});
