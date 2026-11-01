import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthAggDash } from "@/components/health-agg-dash";

describe("HealthAggDash", () => {
  it("renders", () => {
    const { container } = render(
      <HealthAggDash overall="degraded" uptimePct={66.7} avgLatencyMs={12} trend="improving"
        checks={[
          { name: "api", status: "up", latencyMs: 10 },
          { name: "db", status: "down", latencyMs: 0 },
          { name: "cache", status: "up", latencyMs: 2 },
        ]} />
    );
    expect(container.textContent).toContain("System Health");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("66.7%");
    expect(container.textContent).toContain("12ms");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
  });
});
