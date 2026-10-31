import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-webhook-delivery-window-card";

describe("WebhookDeliveryWindowCard", () => {
  it("shows windows", () => {
    const windows = [{ id: "w1", webhookId: "wh1", startHour: 9, endHour: 17, days: [0, 1, 2, 3, 4], enabled: true }];
    const { container } = render(<Card windows={windows} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Delivery Windows");
    expect(container.textContent).toContain("9:00 — 17:00");
    expect(container.textContent).toContain("Mon");
  });
  it("shows always deliver", () => {
    const { container } = render(<Card windows={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("always deliver");
  });
});
