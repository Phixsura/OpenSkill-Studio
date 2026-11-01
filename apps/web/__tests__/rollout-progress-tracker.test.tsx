import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RolloutProgressTracker } from "@/components/rollout-progress-tracker";

describe("RolloutProgressTracker", () => {
  it("renders rollouts", () => {
    const { container } = render(
      <RolloutProgressTracker onAdvance={vi.fn()} onPause={vi.fn()} rollouts={[
        { deploymentId: "d1", currentPct: 50, status: "in_progress", steps: [10, 50, 100], currentStep: 2 },
        { deploymentId: "d2", currentPct: 100, status: "complete", steps: [100], currentStep: 1 },
      ]} />
    );
    expect(container.textContent).toContain("Rollout Tracker");
    expect(container.textContent).toContain("2 rollouts");
    expect(container.textContent).toContain("d1");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("d2");
    expect(container.textContent).toContain("100%");
  });
});
