import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookDebuggerPanel } from "@/components/webhook-debugger-panel";

const mockDeliveries = [
  { id: "d1", eventType: "extension.published", url: "https://hook.test/a", status: "delivered" as const,
    statusCode: 200, attempt: 1, maxAttempts: 5, durationMs: 45, timestamp: "2m ago",
    requestBody: '{"event":"published"}', responseBody: '{"ok":true}' },
  { id: "d2", eventType: "install.created", url: "https://hook.test/b", status: "failed" as const,
    statusCode: 500, attempt: 3, maxAttempts: 5, durationMs: 120, timestamp: "5m ago",
    requestBody: '{"event":"install"}', responseBody: '{"error":"timeout"}' },
];

describe("WebhookDebuggerPanel", () => {
  it("renders deliveries with status badges", () => {
    const { container } = render(<WebhookDebuggerPanel deliveries={mockDeliveries} />);
    expect(container.textContent).toContain("Webhook Debugger");
    expect(container.textContent).toContain("extension.published");
    expect(container.textContent).toContain("delivered");
    expect(container.textContent).toContain("failed");
  });

  it("filters by status", () => {
    const { container, getByText } = render(<WebhookDebuggerPanel deliveries={mockDeliveries} />);
    fireEvent.click(getByText("failed"));
    expect(container.textContent).toContain("1 deliveries");
  });

  it("expands to show request/response", () => {
    const { container, getByText } = render(<WebhookDebuggerPanel deliveries={mockDeliveries} />);
    fireEvent.click(getByText("extension.published"));
    expect(container.textContent).toContain("Request Body");
    expect(container.textContent).toContain('"event":"published"');
  });
});
