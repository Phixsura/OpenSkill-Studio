import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BatchJobTracker } from "@/components/batch-job-tracker";

describe("BatchJobTracker", () => {
  it("renders jobs", () => {
    const { container } = render(
      <BatchJobTracker running={1} totalItems={300} jobs={[
        { jobId: "a1", name: "Export Users", itemCount: 100, totalBatches: 1,
          completedBatches: 1, failedBatches: 0, status: "completed" },
        { jobId: "b2", name: "Process Orders", itemCount: 200, totalBatches: 2,
          completedBatches: 1, failedBatches: 0, status: "running" },
      ]} />
    );
    expect(container.textContent).toContain("Batch Jobs");
    expect(container.textContent).toContain("2 jobs");
    expect(container.textContent).toContain("1 running");
    expect(container.textContent).toContain("Export Users");
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("Process Orders");
  });
});
