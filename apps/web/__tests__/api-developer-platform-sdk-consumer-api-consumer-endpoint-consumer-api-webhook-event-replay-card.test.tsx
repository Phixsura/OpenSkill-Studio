import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-consumer-api-webhook-event-replay-card";

describe("WebhookEventReplayCard", () => {
  it("shows events and replays", () => {
    const events = [{ id: "e1", eventType: "order.created", originalStatus: 200, originalAt: "12:00" }];
    const replays = [{ replayId: "rp1", eventId: "e1", originalStatus: 200, replayStatus: 200, diffDetected: false }];
    const { container } = render(<Card storedEvents={events} replays={replays} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Event Replay");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("200 → 200");
    expect(container.textContent).toContain("OK");
  });
  it("shows empty", () => {
    const { container } = render(<Card storedEvents={[]} replays={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No stored events");
  });
});
