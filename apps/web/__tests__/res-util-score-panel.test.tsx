import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResUtilScorePanel } from "@/components/res-util-score-panel";
describe("ResUtilScorePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ResUtilScorePanel overallScore={75}
        scores={[
          { name: "api", score: 100, status: "optimal", cpuPct: 55, memoryPct: 55 },
          { name: "idle", score: 50, status: "underused", cpuPct: 5, memoryPct: 10 },
        ]} />
    );
    expect(container.textContent).toContain("Resource Utilization");
    expect(container.textContent).toContain("Score: 75/100");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("optimal");
    expect(container.textContent).toContain("idle");
    expect(container.textContent).toContain("underused");
  });
});
