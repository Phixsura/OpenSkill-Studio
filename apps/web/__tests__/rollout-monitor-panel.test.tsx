import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RolloutMonitorPanel } from "@/components/rollout-monitor-panel";
describe("RolloutMonitorPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RolloutMonitorPanel currentPct={25} health="good" recommendation="continue"
        errorRate={0.5} p99Ms={100} errorOk={true} latencyOk={true} />
    );
    expect(container.textContent).toContain("Rollout 25%");
    expect(container.textContent).toContain("GOOD");
    expect(container.textContent).toContain("0.5%");
    expect(container.textContent).toContain("100ms");
    expect(container.textContent).toContain("CONTINUE");
  });
});
