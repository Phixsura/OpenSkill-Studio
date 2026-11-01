import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-status-page-card";

describe("StatusPageCard", () => {
  it("shows status", () => {
    const components = [{ component_id: "api", name: "API", status: "operational" }, { component_id: "db", name: "Database", status: "degraded" }];
    const incidents = [{ incident_id: "i1", title: "Slow queries", status: "investigating", impact: "degraded" }];
    const { container } = render(<Card components={components} incidents={incidents} overallStatus="degraded" appName="App" />);
    expect(container.textContent).toContain("Status Page");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Slow queries");
  });
  it("shows all operational", () => {
    const { container } = render(<Card components={[{ component_id: "api", name: "API", status: "operational" }]} incidents={[]} overallStatus="operational" appName="App" />);
    expect(container.textContent).toContain("operational");
  });
});
