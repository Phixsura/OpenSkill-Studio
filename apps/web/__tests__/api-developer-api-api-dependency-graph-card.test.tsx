import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDependencyGraphCard from "../src/components/api-developer-api-api-dependency-graph-card";

const services = [
  { service_id: "db", name: "Database", dependencies: [], dependents: ["api"], health: "healthy" },
  { service_id: "api", name: "API Server", dependencies: ["db"], dependents: ["web"], health: "down" },
];

describe("APIDeveloperAPIApiDependencyGraphCard", () => {
  it("shows dependency graph", () => {
    const { container } = render(<APIDeveloperAPIApiDependencyGraphCard services={services} appName="App" />);
    expect(container.textContent).toContain("Dependency Graph");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("1 down");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("1 deps");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDependencyGraphCard services={[]} appName="App" />);
    expect(container.textContent).toContain("No services");
  });
});
