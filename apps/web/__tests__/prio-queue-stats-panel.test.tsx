import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PrioQueueStatsPanel } from "@/components/prio-queue-stats-panel";
describe("PrioQueueStatsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <PrioQueueStatsPanel totalQueued={100} status="warning" pct={60}
        priorities={[
          { priority: "critical", count: 5, avgWaitMs: 10 },
          { priority: "normal", count: 80, avgWaitMs: 200 },
          { priority: "low", count: 15, avgWaitMs: 500 },
        ]} />
    );
    expect(container.textContent).toContain("Queue Analytics");
    expect(container.textContent).toContain("100 queued (60%)");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("5 items");
    expect(container.textContent).toContain("avg 200ms wait");
  });
});
