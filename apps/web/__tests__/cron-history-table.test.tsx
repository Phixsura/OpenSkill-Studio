import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CronHistoryTable } from "@/components/cron-history-table";

describe("CronHistoryTable", () => {
  const executions = [
    { jobName: "sync", status: "success", durationMs: 1200, startedAt: "2026-01-03" },
    { jobName: "report", status: "failed", durationMs: 100, startedAt: "2026-01-01" },
  ];
  it("renders history", () => {
    const { container } = render(
      <CronHistoryTable executions={executions} successRate={66.7} avgDurationMs={600} />
    );
    expect(container.textContent).toContain("sync");
    expect(container.textContent).toContain("report");
    expect(container.textContent).toContain("66.7%");
    expect(container.textContent).toContain("600ms");
  });
});
