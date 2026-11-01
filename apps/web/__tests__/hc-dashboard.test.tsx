import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HcDashboard } from "@/components/hc-dashboard";
describe("HcDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <HcDashboard allHealthy={false} healthPct={75}
        categories={{
          services: { items: [{ name: "api", status: "healthy", latencyMs: 5 }], healthy: 1, total: 1, allHealthy: true },
          infrastructure: { items: [{ name: "db", status: "healthy", latencyMs: 2 }, { name: "cache", status: "degraded", latencyMs: 50 }], healthy: 1, total: 2, allHealthy: false },
        }} />
    );
    expect(container.textContent).toContain("75% Healthy");
    expect(container.textContent).toContain("services");
    expect(container.textContent).toContain("1/1");
    expect(container.textContent).toContain("infrastructure");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("cache");
  });
});
