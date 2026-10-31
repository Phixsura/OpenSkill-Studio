import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventBusMonitor } from "@/components/event-bus-monitor";

const topics = [{ topic: "install", subscriberCount: 3, eventCount: 42 }];
const events = [{ eventId: "evt-1", topic: "install", publisherId: "platform", timestamp: Date.now() }];

describe("EventBusMonitor", () => {
  it("renders topics and events", () => {
    const { container } = render(<EventBusMonitor topics={topics} recentEvents={events} />);
    expect(container.textContent).toContain("install");
    expect(container.textContent).toContain("3 subs");
    expect(container.textContent).toContain("platform");
  });
  it("empty events", () => {
    const { container } = render(<EventBusMonitor topics={[]} recentEvents={[]} />);
    expect(container.textContent).toContain("No events yet");
  });
});
