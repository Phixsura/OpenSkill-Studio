import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookBatchDeliveryCard from "../src/components/api-developer-api-api-webhook-batch-delivery-card";

describe("APIDeveloperAPIApiWebhookBatchDeliveryCard", () => {
  it("shows batch stats", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookBatchDeliveryCard stats={{ batches_sent: 100, events_batched: 5000, pending: 15 }} appName="App" />);
    expect(container.textContent).toContain("Batch Delivery");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("15");
    expect(container.textContent).toContain("50");
  });
});
