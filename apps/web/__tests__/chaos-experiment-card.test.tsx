import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChaosExperimentCard } from "@/components/chaos-experiment-card";

describe("ChaosExperimentCard", () => {
  it("renders experiments", () => {
    const onStart = vi.fn();
    const { container, getByText } = render(
      <ChaosExperimentCard onStart={onStart} experiments={[
        { id: "c1", name: "Kill API", target: "api", faultType: "pod_kill", status: "created", blastRadiusPct: 25 },
        { id: "c2", name: "Slow DB", target: "db", faultType: "latency", status: "completed", blastRadiusPct: 50 },
      ]} />
    );
    expect(container.textContent).toContain("Chaos Experiments");
    expect(container.textContent).toContain("Kill API");
    expect(container.textContent).toContain("25% blast radius");
    expect(container.textContent).toContain("completed");
    fireEvent.click(getByText("Run"));
    expect(onStart).toHaveBeenCalledWith("c1");
  });
});
