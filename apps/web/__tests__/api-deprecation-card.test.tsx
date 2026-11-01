import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeprecationCard from "../src/components/api-deprecation-card";

const endpoints = [
  {
    endpoint_id: "ep1",
    method: "GET",
    path: "/api/v1/users",
    replacement: "/api/v2/users",
    days_until_sunset: 45,
    is_sunset: false,
    request_count: 1200,
  },
  {
    endpoint_id: "ep2",
    method: "POST",
    path: "/api/v1/events",
    replacement: "",
    days_until_sunset: 0,
    is_sunset: true,
    request_count: 50,
  },
];

describe("APIDeprecationCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIDeprecationCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("API Deprecations");
    expect(container.textContent).toContain("2 deprecated");
    expect(container.textContent).toContain("1 sunset");
  });

  it("shows method and path", () => {
    const { container } = render(<APIDeprecationCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/users");
  });

  it("shows days left and sunset", () => {
    const { container } = render(<APIDeprecationCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("45d left");
    expect(container.textContent).toContain("sunset");
  });

  it("shows replacement", () => {
    const { container } = render(<APIDeprecationCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("/api/v2/users");
    expect(container.textContent).toContain("no replacement");
  });

  it("shows empty state", () => {
    const { container } = render(<APIDeprecationCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No deprecations");
  });
});
