import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEndpointHealthCard from "../src/components/api-endpoint-health-card";

const endpoints = [
  { method: "GET", path: "/api/users", total: 1000, error_rate: 0.5, is_degraded: false },
  { method: "POST", path: "/api/orders", total: 500, error_rate: 12.5, is_degraded: true },
];

describe("APIEndpointHealthCard", () => {
  it("renders header and degraded count", () => {
    const { container } = render(<APIEndpointHealthCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("Endpoint Health");
    expect(container.textContent).toContain("1 degraded");
  });

  it("shows methods, paths, error rates", () => {
    const { container } = render(<APIEndpointHealthCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("12.5% err");
  });

  it("shows empty state", () => {
    const { container } = render(<APIEndpointHealthCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoint data");
  });
});
