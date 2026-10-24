import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReliabilityScorePanel } from "@/components/reliability-score-panel";
describe("ReliabilityScorePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReliabilityScorePanel service="api" score={95} grade="A"
        breakdown={{ uptime: 99.9, error_rate: 98, latency: 95, recovery: 95, incidents: 90 }} />
    );
    expect(container.textContent).toContain("Reliability: api");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("uptime");
    expect(container.textContent).toContain("99.9");
    expect(container.textContent).toContain("latency");
  });
});
