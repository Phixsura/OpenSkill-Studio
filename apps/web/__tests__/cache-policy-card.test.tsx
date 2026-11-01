import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CachePolicyCard from "../src/components/cache-policy-card";

const rules = [
  {
    rule_id: "r1",
    path_pattern: "/api/v1/users/*",
    ttl_seconds: 300,
    methods: ["GET"],
    enabled: true,
    hit_rate: 85.5,
    hits: 171,
    misses: 29,
  },
  {
    rule_id: "r2",
    path_pattern: "/api/v1/health",
    ttl_seconds: 60,
    methods: ["GET", "HEAD"],
    enabled: false,
    hit_rate: 0,
    hits: 0,
    misses: 0,
  },
];

describe("CachePolicyCard", () => {
  it("renders header and enabled count", () => {
    const { container } = render(<CachePolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Cache Policy");
    expect(container.textContent).toContain("1/2 enabled");
  });

  it("shows path patterns and TTL", () => {
    const { container } = render(<CachePolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("/api/v1/users/*");
    expect(container.textContent).toContain("300s TTL");
  });

  it("shows methods", () => {
    const { container } = render(<CachePolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("GET, HEAD");
  });

  it("shows hit rate", () => {
    const { container } = render(<CachePolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("85.5% hit rate");
  });

  it("shows empty state", () => {
    const { container } = render(<CachePolicyCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No cache rules");
  });
});
