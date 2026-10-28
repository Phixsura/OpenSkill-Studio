import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DependencyGraphCard from "../src/components/dependency-graph-card";

const services = [
  { service_id: "db", name: "Database", depends_on: [], dependent_count: 2 },
  { service_id: "api", name: "API Gateway", depends_on: ["db", "cache"], dependent_count: 1 },
  { service_id: "cache", name: "Cache", depends_on: [], dependent_count: 1 },
  { service_id: "web", name: "Web App", depends_on: ["api"], dependent_count: 0 },
];

describe("DependencyGraphCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="My App" />,
    );
    expect(container.textContent).toContain("Service Dependencies");
    expect(container.textContent).toContain("My App");
  });

  it("shows service count", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("4 services");
  });

  it("shows circular warning", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={true} appName="App" />,
    );
    expect(container.textContent).toContain("Circular");
  });

  it("renders service names", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("API Gateway");
  });

  it("shows dependency arrows", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("← db");
    expect(container.textContent).toContain("← cache");
  });

  it("shows root label for no dependencies", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("No dependencies (root)");
  });

  it("shows dependent count", () => {
    const { container } = render(
      <DependencyGraphCard services={services} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("2 dependents");
  });

  it("shows empty state", () => {
    const { container } = render(
      <DependencyGraphCard services={[]} hasCircular={false} appName="App" />,
    );
    expect(container.textContent).toContain("No services registered");
  });
});
