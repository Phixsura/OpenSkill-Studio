import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PriorityQueueView } from "@/components/priority-queue-view";

describe("PriorityQueueView", () => {
  it("renders queue stats", () => {
    const stats = { pending: 5, processed: 20, hasCritical: true,
      byPriority: { critical: 1, high: 2, medium: 1, low: 1 } };
    const { container } = render(<PriorityQueueView stats={stats} />);
    expect(container.textContent).toContain("Priority Queue");
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("5 pending");
    expect(container.textContent).toContain("20 processed");
  });
});
