import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookEventLogCard from "../src/components/api-webhook-event-log-card";

const events = [{ event_id: "e1", event_type: "push", destination_count: 3, payload_size: 2048 }];

describe("APIWebhookEventLogCard", () => {
  it("shows events", () => {
    const { container } = render(<APIWebhookEventLogCard events={events} totalCount={100} appName="App" />);
    expect(container.textContent).toContain("Event Log");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("3 dest");
    expect(container.textContent).toContain("2.0KB");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookEventLogCard events={[]} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No events logged");
  });
});
