import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CronJobManager } from "@/components/cron-job-manager";

const jobs = [
  { jobId: "c1", name: "Daily Sync", schedule: "0 0 * * *", handler: "/sync", enabled: true, runCount: 42 },
  { jobId: "c2", name: "Hourly Check", schedule: "0 * * * *", handler: "/check", enabled: false, runCount: 0 },
];

describe("CronJobManager", () => {
  it("renders jobs", () => {
    const { container } = render(<CronJobManager jobs={jobs} />);
    expect(container.textContent).toContain("Daily Sync");
    expect(container.textContent).toContain("0 0 * * *");
    expect(container.textContent).toContain("42 runs");
  });
  it("trigger job", () => {
    const fn = vi.fn();
    const { container } = render(<CronJobManager jobs={jobs} onTrigger={fn} />);
    const triggerBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "▶");
    fireEvent.click(triggerBtns[0]);
    expect(fn).toHaveBeenCalledWith("c1");
  });
});
