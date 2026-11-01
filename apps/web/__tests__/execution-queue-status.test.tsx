import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExecutionQueueStatus } from "@/components/execution-queue-status";

describe("ExecutionQueueStatus", () => {
  it("shows running count", () => {
    const { container } = render(<ExecutionQueueStatus queueDepth={2} runningCount={3} maxConcurrent={5} />);
    expect(container.textContent).toContain("3");
  });

  it("shows queue depth", () => {
    const { container } = render(<ExecutionQueueStatus queueDepth={7} runningCount={5} maxConcurrent={5} />);
    expect(container.textContent).toContain("7");
  });

  it("shows utilization", () => {
    const { container } = render(<ExecutionQueueStatus queueDepth={0} runningCount={3} maxConcurrent={5} />);
    expect(container.textContent).toContain("60%");
  });

  it("shows slots", () => {
    const { container } = render(<ExecutionQueueStatus queueDepth={0} runningCount={2} maxConcurrent={5} />);
    expect(container.textContent).toContain("2/5");
  });
});
