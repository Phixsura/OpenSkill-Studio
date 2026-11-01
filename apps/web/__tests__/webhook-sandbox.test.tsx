import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSandbox } from "@/components/webhook-sandbox";

describe("WebhookSandbox", () => {
  it("renders sandbox", () => {
    const { container } = render(
      <WebhookSandbox successRate={67} avgResponseMs={42} onSendTest={vi.fn()}
        results={[
          { eventId: "evt_abc", endpoint: "https://x.com", statusCode: 200, responseMs: 30, delivered: true },
          { eventId: "evt_def", endpoint: "https://x.com", statusCode: 500, responseMs: 5000, delivered: false },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Sandbox");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("Send Test");
    expect(container.textContent).toContain("evt_abc");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
});
