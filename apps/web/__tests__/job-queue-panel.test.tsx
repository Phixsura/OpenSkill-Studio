import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { JobQueuePanel } from "@/components/job-queue-panel";

describe("JobQueuePanel", () => {
  it("renders", () => {
    const { container } = render(
      <JobQueuePanel pending={3} completed={10} failed={1}
        jobs={[
          { id: "j1", status: "processing", priority: 5, attempts: 1 },
          { id: "j2", status: "pending", priority: 1, attempts: 0 },
          { id: "j3", status: "failed", priority: 3, attempts: 3 },
        ]} />
    );
    expect(container.textContent).toContain("Job Queue");
    expect(container.textContent).toContain("3 pending");
    expect(container.textContent).toContain("10 done");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("j1");
    expect(container.textContent).toContain("processing");
  });
});
