import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventSchedulerPanel } from "@/components/event-scheduler-panel";

const mockEvents = [
  { id: "e1", name: "Nightly Sync", action: "run_sync", scheduleType: "recurring" as const,
    status: "active" as const, intervalSeconds: 86400, runCount: 30, maxRuns: 0, failureCount: 1 },
  { id: "e2", name: "One-time Report", action: "gen_report", scheduleType: "once" as const,
    status: "completed" as const, intervalSeconds: 0, runCount: 1, maxRuns: 0, failureCount: 0 },
  { id: "e3", name: "Paused Task", action: "check", scheduleType: "recurring" as const,
    status: "paused" as const, intervalSeconds: 3600, runCount: 5, maxRuns: 10, failureCount: 0 },
];

describe("EventSchedulerPanel", () => {
  it("renders events with status", () => {
    const { container } = render(<EventSchedulerPanel events={mockEvents} />);
    expect(container.textContent).toContain("Nightly Sync");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("Every 1d");
  });

  it("shows failure count", () => {
    const { container } = render(<EventSchedulerPanel events={mockEvents} />);
    expect(container.textContent).toContain("1 failures");
  });

  it("calls onPause for active", () => {
    const onPause = vi.fn();
    const { getByText } = render(<EventSchedulerPanel events={mockEvents} onPause={onPause} />);
    fireEvent.click(getByText("Pause"));
    expect(onPause).toHaveBeenCalledWith("e1");
  });

  it("calls onResume for paused", () => {
    const onResume = vi.fn();
    const { getByText } = render(<EventSchedulerPanel events={mockEvents} onResume={onResume} />);
    fireEvent.click(getByText("Resume"));
    expect(onResume).toHaveBeenCalledWith("e3");
  });
});
