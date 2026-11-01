import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTesterPanel } from "@/components/webhook-tester-panel";

describe("WebhookTesterPanel", () => {
  it("renders form fields", () => {
    const { container, getByPlaceholderText } = render(
      <WebhookTesterPanel extensionName="Slack Bot" />
    );
    expect(container.textContent).toContain("Webhook Tester");
    expect(container.textContent).toContain("Slack Bot");
    expect(getByPlaceholderText("https://your-server.com/webhook")).toBeDefined();
  });

  it("shows event type selector", () => {
    const { container } = render(<WebhookTesterPanel extensionName="Test" />);
    expect(container.textContent).toContain("extension.installed");
  });

  it("disables send without URL", () => {
    const { getByText } = render(<WebhookTesterPanel extensionName="Test" />);
    const btn = getByText("🚀 Send Test Webhook");
    expect(btn.hasAttribute("disabled")).toBe(true);
  });

  it("calls onTest with values", () => {
    const onTest = vi.fn();
    const { getByText } = render(
      <WebhookTesterPanel extensionName="Test" webhookUrl="https://test.com/hook" onTest={onTest} />
    );
    fireEvent.click(getByText("🚀 Send Test Webhook"));
    expect(onTest).toHaveBeenCalledWith("https://test.com/hook", "extension.installed", expect.any(String));
  });
});
