import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-delivery-scheduler-card";

describe("WebhookDeliverySchedulerCard", () => {
  it("shows scheduled", () => {
    const scheduled = [{ delivery_id: "d1", consumer_id: "c1", minutes_until: 30, delivered: false }];
    const { container } = render(<Card scheduled={scheduled} pendingCount={1} dueCount={0} appName="App" />);
    expect(container.textContent).toContain("Delivery Scheduler");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("30m");
  });
  it("shows due count", () => {
    const { container } = render(<Card scheduled={[]} pendingCount={0} dueCount={3} appName="App" />);
    expect(container.textContent).toContain("3 due now");
  });
});
