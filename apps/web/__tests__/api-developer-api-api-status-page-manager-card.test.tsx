import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiStatusPageManagerCard from "../src/components/api-developer-api-api-status-page-manager-card";

const components = [
  { component_id: "api", name: "API Server", status: "operational" },
  { component_id: "db", name: "Database", status: "degraded" },
];

describe("APIDeveloperAPIApiStatusPageManagerCard", () => {
  it("shows status page", () => {
    const { container } = render(<APIDeveloperAPIApiStatusPageManagerCard components={components} overallStatus="degraded" appName="App" />);
    expect(container.textContent).toContain("Status Page");
    expect(container.textContent).toContain("DEGRADED");
    expect(container.textContent).toContain("API Server");
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("Database");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiStatusPageManagerCard components={[]} overallStatus="operational" appName="App" />);
    expect(container.textContent).toContain("No components");
  });
});
