import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiWebhookDeliveryPriorityCard from "../src/components/api-developer-platform-sdk-api-webhook-delivery-priority-card";

const queues = [{ destination: "https://api.example.com", queued: { critical: 2, high: 5, normal: 20, low: 10, bulk: 0 }, delivered: { critical: 100, high: 500, normal: 5000, low: 1000, bulk: 200 }, total_queued: 37, total_delivered: 6800 }];

describe("Card", () => {
  it("shows priority queues", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookDeliveryPriorityCard queues={queues} appName="App" />);
    expect(container.textContent).toContain("Delivery Priority");
    expect(container.textContent).toContain("37 queued");
    expect(container.textContent).toContain("6800 delivered");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookDeliveryPriorityCard queues={[]} appName="App" />);
    expect(container.textContent).toContain("No priority queues");
  });
});
