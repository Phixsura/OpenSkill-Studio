import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEndpointVersionCard from "../src/components/api-endpoint-version-card";

const endpoints = [
  { method: "GET", path: "/api/users", version: "v2", deprecated: false },
  { method: "GET", path: "/api/old", version: "v1", deprecated: true },
];

describe("APIEndpointVersionCard", () => {
  it("renders header and deprecated count", () => {
    const { container } = render(<APIEndpointVersionCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("Endpoint Versions");
    expect(container.textContent).toContain("1 deprecated");
  });

  it("shows endpoints and versions", () => {
    const { container } = render(<APIEndpointVersionCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("v2");
  });

  it("shows empty state", () => {
    const { container } = render(<APIEndpointVersionCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoint versions");
  });
});
