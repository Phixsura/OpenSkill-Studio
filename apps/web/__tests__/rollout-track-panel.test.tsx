import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RolloutTrackPanel } from "@/components/rollout-track-panel";

describe("RolloutTrackPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RolloutTrackPanel rollouts={[
        { name: "v2.0", currentPct: 50, targetPct: 100, status: "in_progress", stepsCompleted: 2 },
        { name: "v1.9", currentPct: 100, targetPct: 100, status: "completed", stepsCompleted: 4 },
      ]} />
    );
    expect(container.textContent).toContain("Rollouts");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("in_progress");
    expect(container.textContent).toContain("50%/100%");
    expect(container.textContent).toContain("completed");
  });
});
