import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QueueRebalancePanel } from "@/components/queue-rebalance-panel";
describe("QueueRebalancePanel", () => {
  it("renders", () => {
    const { container } = render(
      <QueueRebalancePanel totalQueued={100} rebalanceNeeded={true}
        queues={[
          { name: "high", current: 90, action: "decrease", diff: -0.4 },
          { name: "normal", current: 10, action: "increase", diff: 0.4 },
        ]} />
    );
    expect(container.textContent).toContain("Queue Rebalancer");
    expect(container.textContent).toContain("Rebalance needed");
    expect(container.textContent).toContain("100 queued");
    expect(container.textContent).toContain("high (90)");
    expect(container.textContent).toContain("decrease");
    expect(container.textContent).toContain("increase");
  });
});
