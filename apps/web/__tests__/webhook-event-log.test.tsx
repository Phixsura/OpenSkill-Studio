import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookEventLog } from "@/components/webhook-event-log";

const events = [
  { eventId: "wh-1", endpointUrl: "https://api.example.com/hook", status: "delivered", responseCode: 200, attempts: 1, createdAt: Date.now() },
  { eventId: "wh-2", endpointUrl: "https://api.example.com/hook", status: "failed", responseCode: 500, attempts: 2, createdAt: Date.now() },
];

describe("WebhookEventLog", () => {
  it("renders events", () => {
    const { container } = render(<WebhookEventLog events={events} />);
    expect(container.textContent).toContain("delivered");
    expect(container.textContent).toContain("failed");
    expect(container.textContent).toContain("500");
  });
  it("replay failed", () => {
    const fn = vi.fn();
    const { container } = render(<WebhookEventLog events={events} onReplay={fn} />);
    const btn = container.querySelector("button");
    if (btn) fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("wh-2");
  });
});
