import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookLogViewer } from "@/components/webhook-log-viewer";

const mockEntries = [
  { id: "l1", direction: "outbound" as const, eventType: "deploy", endpointUrl: "https://a.com",
    status: "success" as const, statusCode: 200, latencyMs: 45, payloadSizeBytes: 2048, timestamp: "" },
  { id: "l2", direction: "inbound" as const, eventType: "push", endpointUrl: "https://a.com",
    status: "failed" as const, statusCode: 500, latencyMs: 120, payloadSizeBytes: 512,
    errorMessage: "timeout", timestamp: "" },
];
const mockStats = { total: 100, successRate: 95.5, avgLatencyMs: 42 };

describe("WebhookLogViewer", () => {
  it("renders log entries and stats", () => {
    const { container } = render(<WebhookLogViewer entries={mockEntries} stats={mockStats} />);
    expect(container.textContent).toContain("100 events");
    expect(container.textContent).toContain("95.5% success");
    expect(container.textContent).toContain("deploy");
  });

  it("filters by status", () => {
    const onFilter = vi.fn();
    const { getByText, container } = render(
      <WebhookLogViewer entries={mockEntries} stats={mockStats} onFilter={onFilter} />
    );
    fireEvent.click(getByText("failed"));
    expect(onFilter).toHaveBeenCalledWith("failed");
  });

  it("shows direction icons", () => {
    const { container } = render(<WebhookLogViewer entries={mockEntries} stats={mockStats} />);
    expect(container.textContent).toContain("📤");
    expect(container.textContent).toContain("📥");
  });
});
