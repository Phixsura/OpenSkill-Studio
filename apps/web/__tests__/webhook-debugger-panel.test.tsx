import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookDebuggerPanel } from "@/components/webhook-debugger-panel";

describe("WebhookDebuggerPanel", () => {
  const deliveries = [
    { payload_size: 256, content_type: "application/json", has_signature: true,
      signature_valid: true, timestamp: "2026-10-23T12:00:00" },
  ];
  it("renders", () => {
    const { container } = render(
      <WebhookDebuggerPanel endpointUrl="https://debug.openskill.dev/hooks/abc"
        deliveries={deliveries} totalDeliveries={1} onCopyUrl={vi.fn()} />
    );
    expect(container.textContent).toContain("Webhook Debugger");
    expect(container.textContent).toContain("debug.openskill.dev");
    expect(container.textContent).toContain("1 received");
    expect(container.textContent).toContain("256B");
    expect(container.textContent).toContain("✅ sig");
  });
});
