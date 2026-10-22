import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScheduledTasksList } from "@/components/scheduled-tasks-list";

describe("ScheduledTasksList", () => {
  it("renders tasks", () => {
    const tasks = [{ name: "sync", cron: "0 * * * *", description: "Every hour" }];
    const { container } = render(<ScheduledTasksList tasks={tasks} onPause={vi.fn()} />);
    expect(container.textContent).toContain("sync");
    expect(container.textContent).toContain("Every hour");
  });
  it("empty state", () => {
    const { container } = render(<ScheduledTasksList tasks={[]} onPause={vi.fn()} />);
    expect(container.textContent).toContain("No scheduled tasks");
  });
  it("calls onPause", () => {
    const fn = vi.fn();
    const tasks = [{ name: "sync", cron: "0 * * * *", description: "Hourly" }];
    const { container } = render(<ScheduledTasksList tasks={tasks} onPause={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("sync");
  });
});
