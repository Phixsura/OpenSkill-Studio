import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScoreWidget } from "@/components/health-score-widget";

describe("HealthScoreWidget", () => {
  it("renders", () => {
    const { container } = render(
      <HealthScoreWidget score={92.5} grade="A"
        breakdown={{ uptime: 100, error_rate: 98, latency: 95, saturation: 60, freshness: 95 }} />
    );
    expect(container.textContent).toContain("Health Score");
    expect(container.textContent).toContain("92.5");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("uptime");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("saturation");
  });
});
