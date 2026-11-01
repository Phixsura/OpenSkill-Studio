import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChaosExperimentCard } from "@/components/chaos-experiment-card";

describe("ChaosExperimentCard", () => {
  it("renders experiment", () => {
    const { container } = render(
      <ChaosExperimentCard name="Latency Test" target="api" faultType="latency"
        durationSec={120} magnitude={2} status="ready" resilient={null}
        onRun={vi.fn()} onStop={vi.fn()} />
    );
    expect(container.textContent).toContain("Latency Test");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("latency");
    expect(container.textContent).toContain("120s");
    expect(container.textContent).toContain("Run");
  });
});
