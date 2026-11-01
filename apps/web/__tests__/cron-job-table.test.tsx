import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CronJobTable } from "@/components/cron-job-table";

describe("CronJobTable", () => {
  it("renders jobs", () => {
    const onToggle = vi.fn();
    const { container, getAllByRole } = render(
      <CronJobTable onToggle={onToggle} jobs={[
        { id: "j1", name: "Cleanup", schedule: "0 * * * *", enabled: true, lastStatus: "success", runCount: 3, failCount: 1, successRate: 67 },
      ]} />
    );
    expect(container.textContent).toContain("Cron Jobs");
    expect(container.textContent).toContain("Cleanup");
    expect(container.textContent).toContain("0 * * * *");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("success");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onToggle).toHaveBeenCalledWith("j1");
  });
});
