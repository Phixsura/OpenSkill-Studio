import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EndpointHealthTable } from "@/components/endpoint-health-table";

const EPS = [
  { endpoint: "https://a.com/hook", status: "healthy", successRate: 99.5, avgMs: 120, total: 500 },
  { endpoint: "https://b.com/hook", status: "degraded", successRate: 85, avgMs: 800, total: 200 },
];

describe("EndpointHealthTable", () => {
  it("shows endpoints", () => {
    const { container } = render(<EndpointHealthTable endpoints={EPS} />);
    expect(container.textContent).toContain("a.com");
    expect(container.textContent).toContain("b.com");
  });
  it("shows status", () => {
    const { container } = render(<EndpointHealthTable endpoints={EPS} />);
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("degraded");
  });
  it("empty state", () => {
    const { container } = render(<EndpointHealthTable endpoints={[]} />);
    expect(container.textContent).toContain("No endpoint");
  });
});
