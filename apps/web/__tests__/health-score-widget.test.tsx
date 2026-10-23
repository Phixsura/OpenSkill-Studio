import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScoreWidget } from "@/components/health-score-widget";

describe("HealthScoreWidget", () => {
  const signals = {
    uptime: { raw: 99.9, normalized: 99.9, weighted: 30, weight: 30 },
    error_rate: { raw: 0.5, normalized: 99.5, weighted: 24.9, weight: 25 },
  };
  it("renders", () => {
    const { container } = render(
      <HealthScoreWidget score={95} grade="A" status="healthy" signals={signals} />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("95/100");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("Error Rate");
  });
});
