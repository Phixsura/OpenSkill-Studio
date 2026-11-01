import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CronMonitorPanel } from "@/components/cron-monitor-panel";
describe("CronMonitorPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CronMonitorPanel successRate={66.7} totalRuns={3}
        jobs={[
          { name: "cleanup", schedule: "0 * * * *", runs: 2, failures: 0, lastStatus: "success" },
          { name: "report", schedule: "0 9 * * *", runs: 1, failures: 1, lastStatus: "failed" },
        ]} />
    );
    expect(container.textContent).toContain("Cron Monitor");
    expect(container.textContent).toContain("3 runs");
    expect(container.textContent).toContain("66.7% success");
    expect(container.textContent).toContain("cleanup");
    expect(container.textContent).toContain("0 * * * *");
    expect(container.textContent).toContain("report");
    expect(container.textContent).toContain("1 fails");
  });
});
