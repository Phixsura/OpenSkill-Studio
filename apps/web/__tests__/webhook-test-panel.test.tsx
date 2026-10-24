import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTestPanel } from "@/components/webhook-test-panel";

describe("WebhookTestPanel", () => {
  it("renders form", () => {
    const { container } = render(<WebhookTestPanel secret="whsec_abc123def456" onTest={vi.fn()} />);
    expect(container.textContent).toContain("Test Webhook");
    expect(container.textContent).toContain("Send Test Event");
    expect(container.textContent).toContain("whsec_abc123");
    expect(container.querySelector("select")).toBeTruthy();
  });
});
