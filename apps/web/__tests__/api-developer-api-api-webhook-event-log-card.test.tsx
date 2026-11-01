import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookEventLogCard from "../src/components/api-developer-api-api-webhook-event-log-card";

const entries = [
  { event_id: "e1", event_type: "push", destination: "https://a.com", status: "delivered", payload_size_bytes: 512 },
  { event_id: "e2", event_type: "issue", destination: "https://a.com", status: "failed", payload_size_bytes: 256 },
];

describe("APIDeveloperAPIApiWebhookEventLogCard", () => {
  it("shows event log", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookEventLogCard entries={entries} summary={{ delivered: 50, failed: 5 }} totalCount={55} appName="App" />);
    expect(container.textContent).toContain("Event Log");
    expect(container.textContent).toContain("55 events");
    expect(container.textContent).toContain("delivered: 50");
    expect(container.textContent).toContain("push");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookEventLogCard entries={[]} summary={{}} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No events");
  });
});
