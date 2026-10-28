import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DependencyGraphCard from "../src/components/dependency-graph-card";

const services = [
  { service_id: "db", name: "Database", version: "v14", depends_on: [] },
  { service_id: "api", name: "API", version: "v2.1", depends_on: ["db", "cache"] },
  { service_id: "cache", name: "Cache", version: "", depends_on: [] },
  { service_id: "web", name: "Web App", version: "v3.0", depends_on: ["api"] },
];

describe("DependencyGraphCard", () => {
  it("renders header and service count", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("Dependency Graph");
    expect(container.textContent).toContain("4 services");
  });

  it("shows edge count", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("Edges");
  });

  it("shows circular warning", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={true} appName="App" />,
    );
    expect(container.textContent).toContain("Circular detected");
  });

  it("shows dependency counts per service", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("2 deps");
    expect(container.textContent).toContain("no deps");
  });

  it("shows empty state", () => {
    const { container } = render(
      <DependencyGraphCard services={[]} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("No services registered");
  });
});
