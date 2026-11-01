import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PaymentWebhookLog } from "@/components/payment-webhook-log";

describe("PaymentWebhookLog", () => {
  it("renders events", () => {
    const { container } = render(
      <PaymentWebhookLog total={3} events={[
        { event: "payment.completed", amount: 9900, currency: "USD", customer: "cus_123", action: "activate" },
        { event: "refund.created", amount: 2500, currency: "USD", customer: "cus_456", action: "refund" },
      ]} />
    );
    expect(container.textContent).toContain("Payment Webhooks");
    expect(container.textContent).toContain("3 events");
    expect(container.textContent).toContain("payment.completed");
    expect(container.textContent).toContain("99.00 USD");
    expect(container.textContent).toContain("refund.created");
  });
});
