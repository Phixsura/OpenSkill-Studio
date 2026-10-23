import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookDeliveryLog } from "@/components/webhook-delivery-log";

describe("WebhookDeliveryLog", () => {
  const deliveries = [
    { delivery_id: "d1", event: "app.installed", url: "https://x.com", status_code: 200,
      response_time_ms: 120, success: true, timestamp: "2026-10-23T12:00:00" },
    { delivery_id: "d2", event: "review.created", url: "https://x.com", status_code: 500,
      response_time_ms: 5000, success: false, timestamp: "2026-10-23T11:00:00" },
  ];
  it("renders", () => {
    const { container } = render(<WebhookDeliveryLog deliveries={deliveries} successRate={50} />);
    expect(container.textContent).toContain("Webhook Deliveries");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("app.installed");
  });
});
