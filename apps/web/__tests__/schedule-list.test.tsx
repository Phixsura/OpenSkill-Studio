import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScheduleList } from "@/components/schedule-list";

const SCHEDULES = [
  { id: "s1", functionName: "sync_data", cron: "0 * * * *", enabled: true, lastRun: "2026-01-01", runCount: 42 },
  { id: "s2", functionName: "cleanup", cron: "0 0 * * *", enabled: false, lastRun: null, runCount: 0 },
];

describe("ScheduleList", () => {
  it("shows schedules", () => {
    const { container } = render(<ScheduleList schedules={SCHEDULES} />);
    expect(container.textContent).toContain("sync_data");
    expect(container.textContent).toContain("cleanup");
  });

  it("shows empty state", () => {
    const { container } = render(<ScheduleList schedules={[]} />);
    expect(container.textContent).toContain("No scheduled");
  });

  it("shows run count", () => {
    const { container } = render(<ScheduleList schedules={SCHEDULES} />);
    expect(container.textContent).toContain("42 runs");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { container } = render(<ScheduleList schedules={SCHEDULES} onToggle={onToggle} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Disable");
    fireEvent.click(btn!);
    expect(onToggle).toHaveBeenCalledWith("s1", false);
  });
});
