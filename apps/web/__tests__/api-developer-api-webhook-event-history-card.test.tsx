import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookEventHistoryCard from "../src/components/api-developer-api-webhook-event-history-card";

const entries = [
  { event_id: "e1", event_type: "push", destination: "https://a.com", status: "delivered", latency_ms: 50 },
  { event_id: "e2", event_type: "issue", destination: "https://b.com", status: "failed", latency_ms: 3000 },
];

describe("APIDeveloperAPIWebhookEventHistoryCard", () => {
  it("shows history", () => {
    const { container } = render(<APIDeveloperAPIWebhookEventHistoryCard entries={entries} totalCount={500} appName="App" />);
    expect(container.textContent).toContain("Event History");
    expect(container.textContent).toContain("500 events");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("delivered");
    expect(container.textContent).toContain("50ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookEventHistoryCard entries={[]} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No event history");
  });
});
