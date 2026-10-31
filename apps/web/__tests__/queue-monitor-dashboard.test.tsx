import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QueueMonitorDashboard } from "@/components/queue-monitor-dashboard";

describe("QueueMonitorDashboard", () => {
  const queues = [
    { name: "email", pending: 50, processing: 5, failed: 1, completed: 1000,
      throughput_per_min: 20, eta_min: 2.5, healthy: true },
  ];
  it("renders", () => {
    const { container } = render(
      <QueueMonitorDashboard queues={queues} totalBacklog={50} allHealthy={true} />
    );
    expect(container.textContent).toContain("Job Queues");
    expect(container.textContent).toContain("50 pending");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("20/min");
    expect(container.textContent).toContain("ETA: 2.5 min");
  });
});
