import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookPlaygroundPanel } from "@/components/webhook-playground-panel";

describe("WebhookPlaygroundPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WebhookPlaygroundPanel testEndpointUrl="https://webhook.test/abc" receivedCount={5} onSendTest={vi.fn()} />
    );
    expect(container.textContent).toContain("Webhook Playground");
    expect(container.textContent).toContain("webhook.test/abc");
    expect(container.textContent).toContain("5 webhooks received");
  });
  it("sends test", () => {
    const fn = vi.fn();
    const { container } = render(
      <WebhookPlaygroundPanel testEndpointUrl="x" receivedCount={0} onSendTest={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Send Test")!);
    expect(fn).toHaveBeenCalledWith("app.installed");
  });
});
