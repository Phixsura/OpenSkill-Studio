import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookDeliveryPanel } from "@/components/webhook-delivery-panel";

const mockDeliveries = [
  { id: "d1", url: "https://hooks.example.com", state: "delivered" as const,
    attempts: 1, maxRetries: 5, lastStatusCode: 200, createdAt: "2024-01-01" },
  { id: "d2", url: "https://hooks.example.com", state: "dead_letter" as const,
    attempts: 5, maxRetries: 5, lastStatusCode: 500, lastError: "timeout", createdAt: "2024-01-01" },
];
const mockEndpoints = [
  { endpointId: "ep-1", url: "https://hooks.example.com", circuitState: "open" as const,
    consecutiveFailures: 5, totalDeliveries: 100, totalFailures: 10 },
];

describe("WebhookDeliveryPanel", () => {
  it("renders deliveries", () => {
    const { container } = render(
      <WebhookDeliveryPanel deliveries={mockDeliveries} endpoints={mockEndpoints} />
    );
    expect(container.textContent).toContain("delivered");
    expect(container.textContent).toContain("dead_letter");
  });

  it("shows retry button for dead letters", () => {
    const onRetry = vi.fn();
    const { getByText } = render(
      <WebhookDeliveryPanel deliveries={mockDeliveries} endpoints={mockEndpoints} onRetryDeadLetter={onRetry} />
    );
    fireEvent.click(getByText("Retry"));
    expect(onRetry).toHaveBeenCalledWith("d2");
  });

  it("shows endpoints with circuit state", () => {
    const onReset = vi.fn();
    const { getByText, container } = render(
      <WebhookDeliveryPanel deliveries={mockDeliveries} endpoints={mockEndpoints} onResetCircuit={onReset} />
    );
    fireEvent.click(getByText("Endpoints (1)"));
    expect(container.textContent).toContain("open");
    fireEvent.click(getByText("Reset"));
    expect(onReset).toHaveBeenCalledWith("ep-1");
  });
});
