import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EndpointDiscoveryCard from "../src/components/endpoint-discovery-card";

const endpoints = [
  {
    method: "GET",
    path: "/api/users",
    description: "List users",
    auth_required: true,
    rate_limited: true,
    deprecated: false,
    tags: ["users"],
  },
  {
    method: "POST",
    path: "/api/orders",
    description: "Create order",
    auth_required: true,
    rate_limited: false,
    deprecated: false,
    tags: [],
  },
  {
    method: "GET",
    path: "/api/v1/legacy",
    description: "Old endpoint",
    auth_required: false,
    rate_limited: false,
    deprecated: true,
    tags: [],
  },
];

describe("EndpointDiscoveryCard", () => {
  it("renders header", () => {
    const { container } = render(<EndpointDiscoveryCard endpoints={endpoints} appName="My App" />);
    expect(container.textContent).toContain("Endpoint Discovery");
  });

  it("shows endpoint and deprecated counts", () => {
    const { container } = render(<EndpointDiscoveryCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("3 endpoints");
    expect(container.textContent).toContain("1 deprecated");
  });

  it("renders methods and paths", () => {
    const { container } = render(<EndpointDiscoveryCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("POST");
  });

  it("shows auth and rate limit icons", () => {
    const { container } = render(<EndpointDiscoveryCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("🔒");
    expect(container.textContent).toContain("⏱");
  });

  it("shows empty state", () => {
    const { container } = render(<EndpointDiscoveryCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoints discovered");
  });
});
