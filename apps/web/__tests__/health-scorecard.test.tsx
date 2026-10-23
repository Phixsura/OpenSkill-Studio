import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScorecard } from "@/components/health-scorecard";

describe("HealthScorecard", () => {
  it("renders scorecard", () => {
    const { container } = render(
      <HealthScorecard overallDisplay="82/100" overallStatus="good" needsAttention={true}
        dimensions={[
          { name: "Uptime", score: 99, status: "excellent", details: "" },
          { name: "Reliability", score: 45, status: "poor", details: "High error rate" },
        ]} />
    );
    expect(container.textContent).toContain("82/100");
    expect(container.textContent).toContain("good");
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("99/100");
    expect(container.textContent).toContain("Reliability");
    expect(container.textContent).toContain("High error rate");
    expect(container.textContent).toContain("need attention");
  });
});
