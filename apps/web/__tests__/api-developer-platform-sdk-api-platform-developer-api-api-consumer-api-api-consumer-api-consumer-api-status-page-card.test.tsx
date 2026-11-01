import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-status-page-card";

describe("ConsumerApiStatusPageCard", () => {
  it("shows status", () => {
    const components = [{ id: "api", name: "API Gateway", status: "operational" }, { id: "db", name: "Database", status: "degraded" }];
    const { container } = render(<Card overallStatus="degraded" components={components} activeIncidents={1} uptime30d={99.8} appName="App" />);
    expect(container.textContent).toContain("Status Page");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("1 active incident");
    expect(container.textContent).toContain("99.8%");
  });
  it("shows all operational", () => {
    const { container } = render(<Card overallStatus="operational" components={[{ id: "api", name: "API", status: "operational" }]} activeIncidents={0} uptime30d={100} appName="App" />);
    expect(container.textContent).toContain("operational");
    expect(container.textContent).not.toContain("active incident");
  });
});
