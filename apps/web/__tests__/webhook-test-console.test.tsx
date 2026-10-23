import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTestConsole } from "@/components/webhook-test-console";

describe("WebhookTestConsole", () => {
  it("renders and sends test", () => {
    const onTest = vi.fn();
    const { container, getByText } = render(
      <WebhookTestConsole onTest={onTest} result={{ valid: true, timestamp: 1000 }} />
    );
    expect(container.textContent).toContain("Webhook Signature Test");
    expect(container.textContent).toContain("Signature verified");
    fireEvent.click(getByText("Send Test"));
    expect(onTest).toHaveBeenCalled();
  });
});
