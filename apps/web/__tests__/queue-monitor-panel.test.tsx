import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QueueMonitorPanel } from "@/components/queue-monitor-panel";

describe("QueueMonitorPanel", () => {
  it("renders queues", () => {
    const { container } = render(
      <QueueMonitorPanel allHealthy={false} queues={[
        { name: "emails", pending: 50, processing: 10, completed: 900, failed: 40, health: "healthy", avgLatencyMs: 150 },
        { name: "webhooks", pending: 2000, processing: 5, completed: 500, failed: 100, health: "critical", avgLatencyMs: 800 },
      ]} />
    );
    expect(container.textContent).toContain("Queue Monitor");
    expect(container.textContent).toContain("Issues Detected");
    expect(container.textContent).toContain("emails");
    expect(container.textContent).toContain("50 pending");
    expect(container.textContent).toContain("webhooks");
    expect(container.textContent).toContain("100 failed");
  });
});
