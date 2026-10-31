import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployScorecard } from "@/components/deploy-scorecard";

describe("DeployScorecard", () => {
  it("renders", () => {
    const { container } = render(
      <DeployScorecard totalScore={92} grade="A"
        breakdown={{ frequency: 100, success_rate: 98, rollback_rate: 90, automation: 95, approval_time: 96 }} />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("92/100");
    expect(container.textContent).toContain("Deployment Scorecard");
    expect(container.textContent).toContain("frequency");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("success rate");
  });
});
