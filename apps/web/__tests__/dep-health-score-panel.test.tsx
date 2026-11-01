import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepHealthScorePanel } from "@/components/dep-health-score-panel";
describe("DepHealthScorePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepHealthScorePanel score={95} status="healthy" weakest="cache"
        details={[
          { name: "cache", score: 92, latencyMs: 3, errorRate: 0.5 },
          { name: "db", score: 98, latencyMs: 5, errorRate: 0.1 },
        ]} />
    );
    expect(container.textContent).toContain("95/100");
    expect(container.textContent).toContain("HEALTHY");
    expect(container.textContent).toContain("weakest: cache");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("98/100");
  });
});
