import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepHealthCheck } from "@/components/dep-health-check";

describe("DepHealthCheck", () => {
  it("renders deps", () => {
    const { container } = render(
      <DepHealthCheck allOk={false} healthyCount={2} total={3}
        dependencies={[
          { name: "postgres", type: "database", healthy: true, latencyMs: 5 },
          { name: "redis", type: "cache", healthy: true, latencyMs: 2 },
          { name: "email-api", type: "service", healthy: false, latencyMs: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Dependencies");
    expect(container.textContent).toContain("1 failing");
    expect(container.textContent).toContain("postgres");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("email-api");
  });
});
