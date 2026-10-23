import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChaosExperimentCard } from "@/components/chaos-experiment-card";

describe("ChaosExperimentCard", () => {
  it("renders experiment", () => {
    const { container } = render(
      <ChaosExperimentCard faultType="latency" target="api" durationSeconds={60} status="ready" onStart={vi.fn()} onStop={vi.fn()} />
    );
    expect(container.textContent).toContain("latency");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("Start");
  });
  it("shows grade", () => {
    const { container } = render(
      <ChaosExperimentCard faultType="error" target="x" durationSeconds={30} status="completed" grade="A" onStart={vi.fn()} onStop={vi.fn()} />
    );
    expect(container.textContent).toContain("A");
  });
  it("start button", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChaosExperimentCard faultType="latency" target="x" durationSeconds={30} status="ready" onStart={fn} onStop={vi.fn()} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
