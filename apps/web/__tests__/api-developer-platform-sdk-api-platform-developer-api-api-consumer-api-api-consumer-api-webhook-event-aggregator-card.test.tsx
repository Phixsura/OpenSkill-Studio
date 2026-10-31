import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-event-aggregator-card";

describe("WebhookEventAggregatorCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", max_batch_size: 50, max_wait_s: 30, enabled: true, pending: 12 }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Event Aggregator");
    expect(container.textContent).toContain("50/batch");
    expect(container.textContent).toContain("12 pending");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No aggregation configs");
  });
});
