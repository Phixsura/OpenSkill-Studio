import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CronJobPanel } from "@/components/cron-job-panel";

const mockJobs = [
  { id: "c1", name: "Cleanup", expression: "every 1h", command: "rm -rf /tmp/*",
    status: "active" as const, runCount: 24, failureCount: 0, nextRunAt: "in 45m" },
  { id: "c2", name: "Sync", expression: "every 5m", command: "sync_data",
    status: "paused" as const, runCount: 100, failureCount: 2 },
  { id: "c3", name: "Broken", expression: "every 10m", command: "fail",
    status: "disabled" as const, runCount: 15, failureCount: 5 },
];

describe("CronJobPanel", () => {
  it("renders jobs with expression", () => {
    const { container } = render(<CronJobPanel jobs={mockJobs} />);
    expect(container.textContent).toContain("Cleanup");
    expect(container.textContent).toContain("every 1h");
    expect(container.textContent).toContain("1/3 active");
  });

  it("shows failure count", () => {
    const { container } = render(<CronJobPanel jobs={mockJobs} />);
    expect(container.textContent).toContain("2 failures");
    expect(container.textContent).toContain("5 failures");
  });

  it("calls onPause", () => {
    const onPause = vi.fn();
    const { getByText } = render(<CronJobPanel jobs={mockJobs} onPause={onPause} />);
    fireEvent.click(getByText("Pause"));
    expect(onPause).toHaveBeenCalledWith("c1");
  });

  it("calls onResume", () => {
    const onResume = vi.fn();
    const { getByText } = render(<CronJobPanel jobs={mockJobs} onResume={onResume} />);
    fireEvent.click(getByText("Resume"));
    expect(onResume).toHaveBeenCalledWith("c2");
  });
});
