import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthComparePanel } from "@/components/health-compare-panel";
describe("HealthComparePanel", () => {
  it("renders", () => {
    const { container } = render(
      <HealthComparePanel service="api" overall="improved"
        changes={{
          uptime_pct: { current: 99.99, previous: 99.5, delta: 0.49, improved: true },
          error_rate_pct: { current: 0.1, previous: 1.0, delta: -0.9, improved: true },
        }} />
    );
    expect(container.textContent).toContain("Health Compare: api");
    expect(container.textContent).toContain("improved");
    expect(container.textContent).toContain("uptime pct");
    expect(container.textContent).toContain("99.99");
    expect(container.textContent).toContain("+0.49");
  });
});
