import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MqMonitorDashboard } from "@/components/mq-monitor-dashboard";

describe("MqMonitorDashboard", () => {
  it("renders queues", () => {
    const { container } = render(
      <MqMonitorDashboard totalDepth={20050} overallHealth="critical" alertCount={2}
        queues={[
          { name: "orders", depth: 50, enqueueRate: 100, dequeueRate: 120, consumers: 3, growing: false, health: "healthy" },
          { name: "dead_letter", depth: 15000, enqueueRate: 5, dequeueRate: 0, consumers: 0, growing: true, health: "critical" },
        ]} />
    );
    expect(container.textContent).toContain("Message Queues");
    expect(container.textContent).toContain("20,050");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("orders");
    expect(container.textContent).toContain("dead_letter");
    expect(container.textContent).toContain("15,000");
  });
});
