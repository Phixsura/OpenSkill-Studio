import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTestingPanel } from "@/components/webhook-testing-panel";

describe("WebhookTestingPanel", () => {
  it("renders without result", () => {
    const { container } = render(
      <WebhookTestingPanel payloadJson='{"type":"test"}' eventType="webhook.test"
        result={null} onSendTest={vi.fn()} />
    );
    expect(container.textContent).toContain("Test Webhook");
    expect(container.textContent).toContain("webhook.test");
    expect(container.textContent).toContain("Send Test Event");
  });
  it("shows success result", () => {
    const result = { success: true, statusCode: 200, responsePreview: "OK", durationMs: 85, verdict: "✅ Success", error: null };
    const { container } = render(
      <WebhookTestingPanel payloadJson="{}" eventType="test" result={result} onSendTest={vi.fn()} />
    );
    expect(container.textContent).toContain("✅ Success");
    expect(container.textContent).toContain("200");
  });
});
