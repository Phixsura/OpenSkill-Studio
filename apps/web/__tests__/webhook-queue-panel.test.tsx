import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookQueuePanel } from "@/components/webhook-queue-panel";

const mockWebhooks = [
  { webhookId: "w1", url: "https://api.example.com/hook", priority: "critical" as const,
    state: "queued" as const, attempt: 0, maxAttempts: 5, payloadSize: 2048 },
  { webhookId: "w2", url: "https://slack.com/webhook", priority: "normal" as const,
    state: "delivering" as const, attempt: 1, maxAttempts: 3, payloadSize: 512 },
  { webhookId: "w3", url: "https://old.com/hook", priority: "low" as const,
    state: "failed" as const, attempt: 5, maxAttempts: 5, payloadSize: 100 },
];
const mockDepth = { total: 3, pending: 1, byState: { queued: 1, delivering: 1, failed: 1 } };

describe("WebhookQueuePanel", () => {
  it("renders queue with depth", () => {
    const { container } = render(<WebhookQueuePanel webhooks={mockWebhooks} depth={mockDepth} />);
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("api.example.com");
  });

  it("shows priority badges", () => {
    const { container } = render(<WebhookQueuePanel webhooks={mockWebhooks} depth={mockDepth} />);
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("normal");
  });

  it("shows state counts", () => {
    const { container } = render(<WebhookQueuePanel webhooks={mockWebhooks} depth={mockDepth} />);
    expect(container.textContent).toContain("queued: 1");
    expect(container.textContent).toContain("failed: 1");
  });

  it("calls onFlush", () => {
    const onFlush = vi.fn();
    const { getByText } = render(<WebhookQueuePanel webhooks={[]} depth={mockDepth} onFlush={onFlush} />);
    fireEvent.click(getByText("Flush"));
    expect(onFlush).toHaveBeenCalled();
  });
});
