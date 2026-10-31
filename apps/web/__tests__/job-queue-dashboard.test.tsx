import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { JobQueueDashboard } from "@/components/job-queue-dashboard";

describe("JobQueueDashboard", () => {
  it("renders queues", () => {
    const { container } = render(
      <JobQueueDashboard queues={[
        { queue: "default", total: 10, byStatus: { completed: 7, pending: 2, failed: 1 } },
        { queue: "email", total: 5, byStatus: { completed: 5 } },
      ]} />
    );
    expect(container.textContent).toContain("Job Queues");
    expect(container.textContent).toContain("15 total jobs");
    expect(container.textContent).toContain("default");
    expect(container.textContent).toContain("completed: 7");
    expect(container.textContent).toContain("failed: 1");
  });
});
