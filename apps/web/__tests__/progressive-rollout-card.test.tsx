import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProgressiveRolloutCard } from "@/components/progressive-rollout-card";

describe("ProgressiveRolloutCard", () => {
  const stages = [{ name: "canary", pct: 5, duration_hours: 2 }, { name: "half", pct: 50, duration_hours: 8 }, { name: "full", pct: 100, duration_hours: 0 }];
  it("renders stages", () => {
    const { container } = render(
      <ProgressiveRolloutCard stages={stages} currentStage={1} status="active" onAdvance={vi.fn()} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("5%");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("100%");
  });
  it("advance button", () => {
    const fn = vi.fn();
    const { container } = render(
      <ProgressiveRolloutCard stages={stages} currentStage={0} status="active" onAdvance={fn} onRollback={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Advance")!);
    expect(fn).toHaveBeenCalled();
  });
});
