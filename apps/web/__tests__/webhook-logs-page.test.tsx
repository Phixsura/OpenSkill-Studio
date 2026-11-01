import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookLogsPage } from "@/components/webhook-logs-page";

describe("WebhookLogsPage", () => {
  const deliveries = [
    { id: "d1", event: "app.installed", url: "https://x.com", statusCode: 200, success: true, durationMs: 50, timestamp: "2026-01-01" },
  ];
  it("renders logs", () => {
    const { container } = render(
      <WebhookLogsPage deliveries={deliveries} total={1} page={1} totalPages={1}
        successRate={100} onPageChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Webhook Logs");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("100%");
  });
});
