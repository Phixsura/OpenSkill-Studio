import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployCountTrendPanel } from "@/components/deploy-count-trend-panel";
describe("DeployCountTrendPanel", () => {
  it("renders", () => {
    const { container } = render(<DeployCountTrendPanel trend="accelerating" recentAvg={11} olderAvg={5.5} />);
    expect(container.textContent).toContain("Deploy Frequency");
    expect(container.textContent).toContain("accelerating");
  });
});
