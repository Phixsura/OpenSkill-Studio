import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-event-bus-card";

describe("ConsumerApiEventBusCard", () => {
  it("shows subs and deliveries", () => {
    const subs = [{ id: "s1", pattern: "order.*", consumerId: "c1", active: true }];
    const deliveries = [{ eventId: "e1", eventType: "order.created", consumerId: "c1", timestamp: "12:00" }];
    const { container } = render(<Card subscriptions={subs} recentDeliveries={deliveries} appName="App" />);
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("order.*");
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("order.created");
  });
  it("shows empty", () => {
    const { container } = render(<Card subscriptions={[]} recentDeliveries={[]} appName="App" />);
    expect(container.textContent).toContain("No subscriptions");
  });
});
