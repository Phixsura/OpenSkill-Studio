import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindowCard from "../src/components/api-developer-api-api-developer-api-api-webhook-delivery-window-card";

const windows = [{ window_id: "business-hours", destination: "https://a.com", start_hour: 9, end_hour: 17, days: [0, 1, 2, 3, 4], queued_count: 15 }];

describe("APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindowCard", () => {
  it("shows windows", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindowCard windows={windows} appName="App" />);
    expect(container.textContent).toContain("Delivery Windows");
    expect(container.textContent).toContain("business-hours");
    expect(container.textContent).toContain("9:00 – 17:00 UTC");
    expect(container.textContent).toContain("15 queued");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindowCard windows={[]} appName="App" />);
    expect(container.textContent).toContain("No delivery windows");
  });
});
