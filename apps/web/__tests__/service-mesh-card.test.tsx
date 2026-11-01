import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ServiceMeshCard from "../src/components/service-mesh-card";

const routes = [
  { source: "api", destination: "db", allowed: true, timeout_ms: 3000, request_count: 1500 },
  { source: "api", destination: "cache", allowed: true, timeout_ms: 1000, request_count: 5000 },
  { source: "worker", destination: "external", allowed: false, timeout_ms: 5000, request_count: 0 },
];

describe("ServiceMeshCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ServiceMeshCard routes={routes} appName="My App" />);
    expect(container.textContent).toContain("Service Mesh");
    expect(container.textContent).toContain("My App");
  });

  it("shows route count and blocked count", () => {
    const { container } = render(<ServiceMeshCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("3 routes");
    expect(container.textContent).toContain("1 blocked");
  });

  it("renders source → destination", () => {
    const { container } = render(<ServiceMeshCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("→");
    expect(container.textContent).toContain("db");
  });

  it("shows timeout", () => {
    const { container } = render(<ServiceMeshCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("3000ms timeout");
  });

  it("shows request count", () => {
    const { container } = render(<ServiceMeshCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("1500 req");
  });

  it("shows empty state", () => {
    const { container } = render(<ServiceMeshCard routes={[]} appName="App" />);
    expect(container.textContent).toContain("No routes configured");
  });
});
