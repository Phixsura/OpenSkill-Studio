import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-webhook-batch-sender-card";

describe("ConsumerApiWebhookBatchSenderCard", () => {
  it("shows configs", () => {
    const configs = [{ webhookId: "w1", maxBatchSize: 50, maxWaitSec: 10, pendingCount: 5, enabled: true }];
    const { container } = render(<Card configs={configs} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Webhook Batching");
    expect(container.textContent).toContain("w1");
    expect(container.textContent).toContain("Max: 50");
    expect(container.textContent).toContain("Pending: 5");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No batch configs");
  });
});
