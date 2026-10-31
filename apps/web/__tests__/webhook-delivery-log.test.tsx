import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookDeliveryLog } from "@/components/webhook-delivery-log";

const MOCK_DELIVERIES = [
  {
    id: "d1",
    event_type: "skill_pack.published",
    url: "https://app.example.com/webhook",
    status: "delivered" as const,
    attempt_count: 1,
    max_attempts: 5,
    next_retry_at: null,
    created_at: "2026-10-28T14:00:00Z",
    attempts: [
      {
        attempt: 1,
        status_code: 200,
        latency_ms: 45,
        error: null,
        timestamp: "2026-10-28T14:00:00Z",
        success: true,
      },
    ],
  },
  {
    id: "d2",
    event_type: "app.installed",
    url: "https://broken.example.com/hook",
    status: "retrying" as const,
    attempt_count: 2,
    max_attempts: 5,
    next_retry_at: "2026-10-28T14:05:00Z",
    created_at: "2026-10-28T13:55:00Z",
    attempts: [
      {
        attempt: 1,
        status_code: 500,
        latency_ms: 120,
        error: "Internal Server Error",
        timestamp: "2026-10-28T13:55:00Z",
        success: false,
      },
      {
        attempt: 2,
        status_code: 502,
        latency_ms: 5000,
        error: "Bad Gateway",
        timestamp: "2026-10-28T14:00:30Z",
        success: false,
      },
    ],
  },
  {
    id: "d3",
    event_type: "workflow.completed",
    url: "https://dead.example.com/hook",
    status: "dead_letter" as const,
    attempt_count: 5,
    max_attempts: 5,
    next_retry_at: null,
    created_at: "2026-10-28T12:00:00Z",
    attempts: [],
  },
];

describe("WebhookDeliveryLog", () => {
  it("renders header with counts", () => {
    const { container } = render(
      <WebhookDeliveryLog
        deliveries={MOCK_DELIVERIES}
        onReplay={vi.fn()}
        onCancel={vi.fn()}
        totalCount={42}
      />,
    );
    expect(container.textContent).toContain("Webhook Deliveries");
    expect(container.textContent).toContain("42 total");
    expect(container.textContent).toContain("1 delivered");
    expect(container.textContent).toContain("2 failing");
  });

  it("renders event types", () => {
    const { container } = render(
      <WebhookDeliveryLog
        deliveries={MOCK_DELIVERIES}
        onReplay={vi.fn()}
        onCancel={vi.fn()}
        totalCount={3}
      />,
    );
    expect(container.textContent).toContain("skill_pack.published");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("workflow.completed");
  });

  it("renders status badges", () => {
    const { container } = render(
      <WebhookDeliveryLog
        deliveries={MOCK_DELIVERIES}
        onReplay={vi.fn()}
        onCancel={vi.fn()}
        totalCount={3}
      />,
    );
    expect(container.textContent).toContain("Delivered");
    expect(container.textContent).toContain("Retrying");
    expect(container.textContent).toContain("Failed");
  });

  it("shows empty state when no deliveries", () => {
    const { container } = render(
      <WebhookDeliveryLog deliveries={[]} onReplay={vi.fn()} onCancel={vi.fn()} totalCount={0} />,
    );
    expect(container.textContent).toContain("No webhook deliveries yet");
  });

  it("expands delivery row on click to show attempts", () => {
    const { container } = render(
      <WebhookDeliveryLog
        deliveries={MOCK_DELIVERIES}
        onReplay={vi.fn()}
        onCancel={vi.fn()}
        totalCount={3}
      />,
    );
    // Click on the retrying delivery (second row)
    const buttons = container.querySelectorAll("button[aria-expanded]");
    expect(buttons.length).toBe(3);
    fireEvent.click(buttons[1]);
    // Should now show attempt details
    expect(container.textContent).toContain("Attempts: 2/5");
    expect(container.textContent).toContain("Internal Server Error");
    expect(container.textContent).toContain("Bad Gateway");
  });

  it("shows Replay button for dead-lettered deliveries", () => {
    const onReplay = vi.fn();
    const { container } = render(
      <WebhookDeliveryLog
        deliveries={MOCK_DELIVERIES}
        onReplay={onReplay}
        onCancel={vi.fn()}
        totalCount={3}
      />,
    );
    // Expand the dead_letter row
    const buttons = container.querySelectorAll("button[aria-expanded]");
    fireEvent.click(buttons[2]);
    const replayBtn = container.querySelector("button")!;
    const allButtons = Array.from(container.querySelectorAll("button"));
    const replay = allButtons.find((b) => b.textContent === "Replay");
    expect(replay).toBeTruthy();
    fireEvent.click(replay!);
    expect(onReplay).toHaveBeenCalledWith("d3");
  });

  it("shows Cancel button for retrying deliveries", () => {
    const onCancel = vi.fn();
    const { container } = render(
      <WebhookDeliveryLog
        deliveries={MOCK_DELIVERIES}
        onReplay={vi.fn()}
        onCancel={onCancel}
        totalCount={3}
      />,
    );
    // Expand the retrying row
    const buttons = container.querySelectorAll("button[aria-expanded]");
    fireEvent.click(buttons[1]);
    const allButtons = Array.from(container.querySelectorAll("button"));
    const cancel = allButtons.find((b) => b.textContent === "Cancel");
    expect(cancel).toBeTruthy();
    fireEvent.click(cancel!);
    expect(onCancel).toHaveBeenCalledWith("d2");
  });

  it("renders attempt table with status codes and latency", () => {
    const { container } = render(
      <WebhookDeliveryLog
        deliveries={MOCK_DELIVERIES}
        onReplay={vi.fn()}
        onCancel={vi.fn()}
        totalCount={3}
      />,
    );
    // Expand the delivered row
    const buttons = container.querySelectorAll("button[aria-expanded]");
    fireEvent.click(buttons[0]);
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("45ms");
  });
});
