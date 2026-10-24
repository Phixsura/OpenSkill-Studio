import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChaosSchedPanel } from "@/components/chaos-sched-panel";

describe("ChaosSchedPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ChaosSchedPanel byStatus={{ running: 1, completed: 1 }}
        experiments={[
          { name: "exp-1", target: "api", faultType: "latency", status: "running", blastRadius: "single" },
          { name: "exp-2", target: "db", faultType: "partition", status: "completed", blastRadius: "zone" },
        ]} />
    );
    expect(container.textContent).toContain("Chaos Scheduler");
    expect(container.textContent).toContain("2 experiments");
    expect(container.textContent).toContain("exp-1");
    expect(container.textContent).toContain("latency");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("completed");
  });
});
