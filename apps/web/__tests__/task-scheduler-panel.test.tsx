import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TaskSchedulerPanel } from "@/components/task-scheduler-panel";

describe("TaskSchedulerPanel", () => {
  it("renders tasks", () => {
    const { container } = render(
      <TaskSchedulerPanel onRun={vi.fn()} onToggle={vi.fn()} tasks={[
        { name: "cleanup", schedule: "0 * * * *", handler: "tasks.cleanup", enabled: true, runCount: 42, lastStatus: "success" },
        { name: "report", schedule: "0 9 * * 1", handler: "tasks.report", enabled: false, runCount: 5, lastStatus: null },
      ]} />
    );
    expect(container.textContent).toContain("Scheduled Tasks");
    expect(container.textContent).toContain("2 tasks");
    expect(container.textContent).toContain("cleanup");
    expect(container.textContent).toContain("42 runs");
    expect(container.textContent).toContain("report");
    expect(container.textContent).toContain("Off");
  });
});
