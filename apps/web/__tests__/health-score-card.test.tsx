import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScoreCard } from "@/components/health-score-card";

describe("HealthScoreCard", () => {
  it("renders score", () => {
    const { container } = render(
      <HealthScoreCard score={92.3} grade="A" status="healthy" delta={5.2}
        breakdown={{
          uptime: { raw: 99, weight: 0.3, weighted: 29.7 },
          error_rate: { raw: 95, weight: 0.25, weighted: 23.75 },
          latency: { raw: 85, weight: 0.2, weighted: 17 },
        }} />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("92.3");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("5.2 pts");
    expect(container.textContent).toContain("uptime");
    expect(container.textContent).toContain("29.7");
  });
});
