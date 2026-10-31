import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TaskQueuePanel } from "@/components/task-queue-panel";

const mockTasks = [
  { taskId: "t1", name: "process_data", state: "running" as const, priority: 5,
    progress: 65, retryCount: 0, maxRetries: 3 },
  { taskId: "t2", name: "send_email", state: "pending" as const, priority: 1,
    progress: 0, retryCount: 0, maxRetries: 3 },
  { taskId: "t3", name: "deploy", state: "waiting" as const, priority: 10,
    progress: 0, retryCount: 0, maxRetries: 2, dependsOn: "t1" },
  { taskId: "t4", name: "broken", state: "failed" as const, priority: 0,
    progress: 0, retryCount: 2, maxRetries: 3, error: "Connection reset" },
];
const mockStats = { total: 4, byState: { running: 1, pending: 1, waiting: 1, failed: 1 } };

describe("TaskQueuePanel", () => {
  it("renders tasks with state", () => {
    const { container } = render(<TaskQueuePanel tasks={mockTasks} stats={mockStats} />);
    expect(container.textContent).toContain("process_data");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("P5");
  });

  it("shows progress bar for running", () => {
    const { container } = render(<TaskQueuePanel tasks={mockTasks} stats={mockStats} />);
    const bars = container.querySelectorAll("[class*='bg-blue-500'][class*='rounded-full']");
    expect(bars.length).toBeGreaterThan(0);
  });

  it("shows dependency chain", () => {
    const { container } = render(<TaskQueuePanel tasks={mockTasks} stats={mockStats} />);
    expect(container.textContent).toContain("⛓ t1");
  });

  it("calls onCancel", () => {
    const onCancel = vi.fn();
    const { getByText } = render(<TaskQueuePanel tasks={mockTasks} stats={mockStats} onCancel={onCancel} />);
    fireEvent.click(getByText("Cancel"));
    expect(onCancel).toHaveBeenCalledWith("t2");
  });
});
