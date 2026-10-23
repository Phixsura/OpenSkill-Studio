import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSecretRotation } from "@/components/webhook-secret-rotation";

describe("WebhookSecretRotation", () => {
  it("renders rotation card", () => {
    const onRotate = vi.fn();
    const { container, getByText } = render(
      <WebhookSecretRotation webhookId="wh_abc123" hasSecret={true}
        lastRotated="2 days ago" gracePeriod="1 hour" onRotate={onRotate} />
    );
    expect(container.textContent).toContain("Webhook Secret");
    expect(container.textContent).toContain("wh_abc123");
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("2 days ago");
    fireEvent.click(getByText("Rotate Secret"));
    expect(onRotate).toHaveBeenCalled();
  });
});
