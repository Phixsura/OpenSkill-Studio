import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScoreBadge } from "@/components/health-score-badge";

const result = { score: 92.5, grade: "A", breakdown: { uptime: 100, error_rate: 90, response_time: 88, update_freq: 100, issues: 85, coverage: 95, security: 100 } };

describe("HealthScoreBadge", () => {
  it("renders score", () => {
    const { container } = render(<HealthScoreBadge result={result} />);
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("92.5");
    expect(container.textContent).toContain("Health Score");
  });
  it("shows breakdown", () => {
    const { container } = render(<HealthScoreBadge result={result} showBreakdown />);
    expect(container.textContent).toContain("uptime");
    expect(container.textContent).toContain("coverage");
  });
});
