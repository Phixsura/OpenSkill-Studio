import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookDeliveryTimelineCard from "../src/components/api-developer-api-webhook-delivery-timeline-card";

const entries = [
  { delivery_id: "d1", event_type: "push", destination: "https://a.com", status: "success", latency_ms: 50 },
  { delivery_id: "d2", event_type: "issue", destination: "https://b.com", status: "failure", latency_ms: 3000 },
];

describe("APIDeveloperAPIWebhookDeliveryTimelineCard", () => {
  it("shows timeline", () => {
    const { container } = render(<APIDeveloperAPIWebhookDeliveryTimelineCard entries={entries} totalCount={100} failureCount={5} appName="App" />);
    expect(container.textContent).toContain("Delivery Timeline");
    expect(container.textContent).toContain("5 failures");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("success");
    expect(container.textContent).toContain("50ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookDeliveryTimelineCard entries={[]} totalCount={0} failureCount={0} appName="App" />);
    expect(container.textContent).toContain("No deliveries");
  });
});
