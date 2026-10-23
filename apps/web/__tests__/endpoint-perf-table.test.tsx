import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EndpointPerfTable } from "@/components/endpoint-perf-table";

describe("EndpointPerfTable", () => {
  it("renders perf", () => {
    const { container } = render(
      <EndpointPerfTable totalRequests={1000} endpoints={[
        { endpoint: "GET /users", total: 500, avgMs: 65, p50Ms: 50, p99Ms: 200, errorRate: 2.5, health: "ok" },
        { endpoint: "POST /apps", total: 500, avgMs: 120, p50Ms: 100, p99Ms: 500, errorRate: 0.5, health: "good" },
      ]} />
    );
    expect(container.textContent).toContain("Endpoint Performance");
    expect(container.textContent).toContain("1,000 requests");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("65ms");
    expect(container.textContent).toContain("2.5%");
    expect(container.textContent).toContain("ok");
  });
});
