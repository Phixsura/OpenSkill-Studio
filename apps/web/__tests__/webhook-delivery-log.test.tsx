import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookDeliveryLog } from "@/components/webhook-delivery-log";

describe("WebhookDeliveryLog", () => {
  it("renders deliveries", () => {
    const { container } = render(
      <WebhookDeliveryLog successRate={67} avgResponseMs={1100}
        deliveries={[
          { endpoint: "https://a.com", event: "install", statusCode: 200, responseMs: 100, success: true },
          { endpoint: "https://a.com", event: "uninstall", statusCode: 500, responseMs: 3000, success: false },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Deliveries");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("install");
    expect(container.textContent).toContain("500");
  });
});
