import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScoreCard } from "@/components/health-score-card";

describe("HealthScoreCard", () => {
  const details = [
    { dimension: "reliability", score: 95, weight: 0.3, weighted: 28.5, description: "Uptime" },
    { dimension: "performance", score: 70, weight: 0.25, weighted: 17.5, description: "Speed" },
  ];
  it("renders health score", () => {
    const { container } = render(
      <HealthScoreCard overall={82} grade="B" status="healthy" details={details} />
    );
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("82/100");
    expect(container.textContent).toContain("reliability");
    expect(container.textContent).toContain("95/100");
  });
});
