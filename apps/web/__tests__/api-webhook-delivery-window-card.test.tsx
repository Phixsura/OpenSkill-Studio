import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookDeliveryWindowCard from "../src/components/api-webhook-delivery-window-card";

const windows = [{ window_id: "w1", destination: "https://a.com", start_hour: 9, end_hour: 17, timezone: "UTC", enabled: true }];

describe("APIWebhookDeliveryWindowCard", () => {
  it("shows windows", () => {
    const { container } = render(<APIWebhookDeliveryWindowCard windows={windows} appName="App" />);
    expect(container.textContent).toContain("Delivery Windows");
    expect(container.textContent).toContain("9:00–17:00 UTC");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookDeliveryWindowCard windows={[]} appName="App" />);
    expect(container.textContent).toContain("No delivery windows");
  });
});
