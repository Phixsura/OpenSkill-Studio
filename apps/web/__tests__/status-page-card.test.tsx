import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StatusPageCard from "../src/components/status-page-card";

const components = [
  { component_id: "api", name: "API", status: "operational" as const },
  { component_id: "db", name: "Database", status: "major_outage" as const },
];
const incidents = [{ incident_id: "inc-1", title: "DB Down", status: "investigating" }];

describe("StatusPageCard", () => {
  it("renders header and overall status", () => {
    const { container } = render(
      <StatusPageCard
        components={components}
        incidents={incidents}
        overallStatus="major_outage"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Status Page");
    expect(container.textContent).toContain("major outage");
  });

  it("shows component names and statuses", () => {
    const { container } = render(
      <StatusPageCard
        components={components}
        incidents={[]}
        overallStatus="operational"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("Database");
  });

  it("shows incidents", () => {
    const { container } = render(
      <StatusPageCard
        components={components}
        incidents={incidents}
        overallStatus="major_outage"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("DB Down");
    expect(container.textContent).toContain("investigating");
  });

  it("shows component count", () => {
    const { container } = render(
      <StatusPageCard
        components={components}
        incidents={[]}
        overallStatus="operational"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("2 components");
  });
});
