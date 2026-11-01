import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CronJobMonitor } from "@/components/cron-job-monitor";

describe("CronJobMonitor", () => {
  it("renders jobs", () => {
    const { container } = render(
      <CronJobMonitor jobs={[
        { name: "cleanup", successRate: 100, avgDuration: 3, consecutiveFailures: 0, healthy: true, runs: 50 },
        { name: "report", successRate: 60, avgDuration: 15, consecutiveFailures: 4, healthy: false, runs: 20 },
      ]} />
    );
    expect(container.textContent).toContain("Cron Jobs");
    expect(container.textContent).toContain("2 jobs");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("cleanup");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("report");
    expect(container.textContent).toContain("4× failed");
  });
});
