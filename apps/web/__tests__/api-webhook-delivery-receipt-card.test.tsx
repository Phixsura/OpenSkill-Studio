import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookDeliveryReceiptCard from "../src/components/api-webhook-delivery-receipt-card";

const receipts = [
  { receipt_id: "r1", destination: "https://a.com", status_code: 200, response_time_ms: 45, acknowledged: true },
  { receipt_id: "r2", destination: "https://b.com", status_code: 500, response_time_ms: 100, acknowledged: false },
];

describe("APIWebhookDeliveryReceiptCard", () => {
  it("shows receipts and rate", () => {
    const { container } = render(<APIWebhookDeliveryReceiptCard receipts={receipts} acknowledgedRate={50} totalCount={100} appName="App" />);
    expect(container.textContent).toContain("Delivery Receipts");
    expect(container.textContent).toContain("50% acknowledged");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("45ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookDeliveryReceiptCard receipts={[]} acknowledgedRate={100} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No receipts");
  });
});
