import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TaskSchedPanel } from "@/components/task-sched-panel";

describe("TaskSchedPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TaskSchedPanel totalExecutions={150} enabledCount={2}
        tasks={[
          { name: "cleanup", interval: 60, enabled: true, runCount: 100, handler: "cleanup_handler" },
          { name: "report", interval: 300, enabled: true, runCount: 50, handler: "report_handler" },
          { name: "archive", interval: 3600, enabled: false, runCount: 0, handler: "archive_handler" },
        ]} />
    );
    expect(container.textContent).toContain("Task Scheduler");
    expect(container.textContent).toContain("2/3 enabled");
    expect(container.textContent).toContain("150 runs");
    expect(container.textContent).toContain("cleanup");
    expect(container.textContent).toContain("every 60s");
    expect(container.textContent).toContain("100 runs");
  });
});
