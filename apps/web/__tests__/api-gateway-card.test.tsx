import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIGatewayCard from "../src/components/api-gateway-card";

const routes = [
  {
    route_id: "r1",
    path_prefix: "/api/users",
    upstream: "http://users-svc:8080",
    strip_prefix: true,
    enabled: true,
    request_count: 500,
  },
  {
    route_id: "r2",
    path_prefix: "/api/apps",
    upstream: "http://apps-svc:8080",
    strip_prefix: true,
    enabled: false,
    request_count: 0,
  },
];

describe("APIGatewayCard", () => {
  it("renders header and summary", () => {
    const { container } = render(<APIGatewayCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("500 reqs");
  });

  it("shows path prefixes and upstreams", () => {
    const { container } = render(<APIGatewayCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("http://users-svc:8080");
  });

  it("shows empty state", () => {
    const { container } = render(<APIGatewayCard routes={[]} appName="App" />);
    expect(container.textContent).toContain("No gateway routes");
  });
});
