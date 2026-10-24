import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SchedExecPanel } from "@/components/sched-exec-panel";
describe("SchedExecPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SchedExecPanel enabled={2} totalRuns={150}
        tasks={[
          { name: "cleanup", schedule: "0 * * * *", enabled: true, runs: 100 },
          { name: "report", schedule: "0 9 * * *", enabled: true, runs: 50 },
          { name: "archive", schedule: "0 0 * * 0", enabled: false, runs: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Scheduled Tasks");
    expect(container.textContent).toContain("2/3 enabled");
    expect(container.textContent).toContain("150 runs");
    expect(container.textContent).toContain("cleanup");
    expect(container.textContent).toContain("0 * * * *");
  });
});
