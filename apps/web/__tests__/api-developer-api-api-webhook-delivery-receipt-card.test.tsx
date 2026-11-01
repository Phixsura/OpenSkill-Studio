import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookDeliveryReceiptCard from "../src/components/api-developer-api-api-webhook-delivery-receipt-card";

const receipts = [
  { delivery_id: "d1", destination: "https://a.com", status_code: 200, acknowledged: true, response_time_ms: 50, retry_number: 0 },
  { delivery_id: "d2", destination: "https://a.com", status_code: 500, acknowledged: false, response_time_ms: 100, retry_number: 2 },
];

describe("APIDeveloperAPIApiWebhookDeliveryReceiptCard", () => {
  it("shows receipts", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookDeliveryReceiptCard receipts={receipts} ackRate={66.7} avgResponseTime={75} unacknowledgedCount={1} appName="App" />);
    expect(container.textContent).toContain("Delivery Receipts");
    expect(container.textContent).toContain("66.7%");
    expect(container.textContent).toContain("1 unacknowledged");
    expect(container.textContent).toContain("retry #2");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookDeliveryReceiptCard receipts={[]} ackRate={100} avgResponseTime={0} unacknowledgedCount={0} appName="App" />);
    expect(container.textContent).toContain("No receipts");
  });
});
