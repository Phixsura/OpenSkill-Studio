import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScheduledTaskManager } from "@/components/scheduled-task-manager";

describe("ScheduledTaskManager", () => {
  const tasks = [
    { task_id: "t1", name: "Cleanup", cron: "0 3 * * *", status: "active", last_run: "2026-10-23", success_count: 42, fail_count: 1 },
  ];
  it("renders", () => {
    const { container } = render(<ScheduledTaskManager tasks={tasks} onToggle={vi.fn()} onDelete={vi.fn()} />);
    expect(container.textContent).toContain("Scheduled Tasks");
    expect(container.textContent).toContain("Cleanup");
    expect(container.textContent).toContain("0 3 * * *");
    expect(container.textContent).toContain("✅ 42");
  });
  it("toggle", () => {
    const fn = vi.fn();
    const { container } = render(<ScheduledTaskManager tasks={tasks} onToggle={fn} onDelete={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Pause")!);
    expect(fn).toHaveBeenCalledWith("t1");
  });
});
