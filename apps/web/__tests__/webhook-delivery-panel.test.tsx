import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookDeliveryPanel } from "@/components/webhook-delivery-panel";

describe("WebhookDeliveryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WebhookDeliveryPanel total={10} successRate={80} failures={2}
        entries={[
          { webhookId: "w1", url: "https://example.com/hook", statusCode: 200, attempt: 1, success: true },
          { webhookId: "w2", url: "https://fail.com/hook", statusCode: 500, attempt: 2, success: false },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Delivery");
    expect(container.textContent).toContain("80% success");
    expect(container.textContent).toContain("10 total");
    expect(container.textContent).toContain("https://example.com/hook");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
});
