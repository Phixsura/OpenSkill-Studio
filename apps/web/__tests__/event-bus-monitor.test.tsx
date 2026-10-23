import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventBusMonitor } from "@/components/event-bus-monitor";

describe("EventBusMonitor", () => {
  const events = [
    { event: "app.installed", subscriberCount: 2, timestamp: "2026-01-01T10:00:00Z" },
  ];
  const subs = [{ handlerId: "h1", name: "Logger", event: "app.installed" }];
  it("renders events", () => {
    const { container } = render(
      <EventBusMonitor events={events} subscriptions={subs} eventTypes={["app.installed"]} />
    );
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("2 subs");
    expect(container.textContent).toContain("1 event types");
  });
});
