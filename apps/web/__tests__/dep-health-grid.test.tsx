import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepHealthGrid } from "@/components/dep-health-grid";

describe("DepHealthGrid", () => {
  it("renders", () => {
    const { container } = render(
      <DepHealthGrid overall="critical"
        dependencies={[
          { name: "database", healthy: false, degraded: false, latencyMs: 0, critical: true },
          { name: "cache", healthy: true, degraded: false, latencyMs: 2, critical: false },
        ]} />
    );
    expect(container.textContent).toContain("Dependency Health");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("CRIT");
    expect(container.textContent).toContain("cache");
    expect(container.textContent).toContain("2ms");
  });
});
