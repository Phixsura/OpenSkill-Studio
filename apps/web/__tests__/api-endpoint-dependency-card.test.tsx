import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEndpointDependencyCard from "../src/components/api-endpoint-dependency-card";

const eps = [
  { method: "POST", path: "/api/orders", dependency_count: 2 },
  { method: "GET", path: "/api/auth", dependency_count: 0 },
];

describe("APIEndpointDependencyCard", () => {
  it("shows deps", () => {
    const { container } = render(<APIEndpointDependencyCard endpoints={eps} appName="App" />);
    expect(container.textContent).toContain("Endpoint Deps");
    expect(container.textContent).toContain("1/2 with deps");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("2 deps");
  });
  it("shows empty", () => {
    const { container } = render(<APIEndpointDependencyCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoint dependencies");
  });
});
