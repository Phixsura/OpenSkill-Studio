import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WorkerPoolDashboard } from "@/components/worker-pool-dashboard";

describe("WorkerPoolDashboard", () => {
  it("renders pools", () => {
    const { container } = render(
      <WorkerPoolDashboard pools={[
        { name: "email", size: 5, active: 2, idle: 3, queueDepth: 0, processed: 500, failureRate: 1, healthy: true },
        { name: "export", size: 3, active: 3, idle: 0, queueDepth: 10, processed: 200, failureRate: 8, healthy: false },
      ]} />
    );
    expect(container.textContent).toContain("Worker Pools");
    expect(container.textContent).toContain("2 pools");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("2/5 active");
    expect(container.textContent).toContain("export");
    expect(container.textContent).toContain("10 queued");
  });
});
