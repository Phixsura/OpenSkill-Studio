import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-event-stream-card";

describe("EventStreamCard", () => {
  it("shows subscriptions", () => {
    const subs = [{ subscription_id: "s1", consumer_id: "c1", transport: "sse", event_types: ["order.created"], events_delivered: 500, active: true }];
    const { container } = render(<Card subscriptions={subs} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Event Stream");
    expect(container.textContent).toContain("sse");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("500 delivered");
  });
  it("shows empty", () => {
    const { container } = render(<Card subscriptions={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No streams");
  });
});
