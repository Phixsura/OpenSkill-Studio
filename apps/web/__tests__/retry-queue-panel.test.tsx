import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RetryQueuePanel } from "@/components/retry-queue-panel";

const mockItems = [
  { id: "r1", operation: "send_webhook", status: "retrying" as const,
    attempt: 2, maxAttempts: 5, strategy: "exponential", lastError: "timeout" },
  { id: "r2", operation: "sync_data", status: "dead_letter" as const,
    attempt: 5, maxAttempts: 5, strategy: "linear", lastError: "connection refused" },
  { id: "r3", operation: "notify", status: "succeeded" as const,
    attempt: 1, maxAttempts: 3, strategy: "fixed" },
];
const mockStats = { total: 3, pending: 0, retrying: 1, succeeded: 1, deadLetter: 1 };

describe("RetryQueuePanel", () => {
  it("renders stats and items", () => {
    const { container } = render(<RetryQueuePanel items={mockItems} stats={mockStats} />);
    expect(container.textContent).toContain("send_webhook");
    expect(container.textContent).toContain("2/5");
    expect(container.textContent).toContain("timeout");
  });

  it("shows stats grid", () => {
    const { container } = render(<RetryQueuePanel items={mockItems} stats={mockStats} />);
    expect(container.textContent).toContain("Retrying");
    expect(container.textContent).toContain("Dead Letter");
  });

  it("filters by status", () => {
    const { getByText, container } = render(<RetryQueuePanel items={mockItems} stats={mockStats} />);
    fireEvent.click(getByText("dead letter"));
    expect(container.textContent).toContain("sync_data");
    expect(container.textContent).not.toContain("send_webhook");
  });

  it("calls onRetryDeadLetter", () => {
    const onRetry = vi.fn();
    const { getByText } = render(
      <RetryQueuePanel items={mockItems} stats={mockStats} onRetryDeadLetter={onRetry} />
    );
    fireEvent.click(getByText("Retry"));
    expect(onRetry).toHaveBeenCalledWith("r2");
  });
});
