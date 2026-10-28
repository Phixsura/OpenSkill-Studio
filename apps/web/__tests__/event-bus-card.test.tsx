import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EventBusCard from "../src/components/event-bus-card";

const subs = [
  {
    subscription_id: "sub-webhook",
    event_types: ["user.created", "user.deleted"],
    active: true,
    delivery_count: 150,
  },
  { subscription_id: "sub-all", event_types: null, active: true, delivery_count: 500 },
];

const events = [
  {
    event_id: "e1",
    event_type: "user.created",
    timestamp: new Date(Date.now() - 60000).toISOString(),
  },
  {
    event_id: "e2",
    event_type: "order.placed",
    timestamp: new Date(Date.now() - 120000).toISOString(),
  },
];

describe("EventBusCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <EventBusCard subscriptions={subs} recentEvents={events} appName="My App" />,
    );
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("My App");
  });

  it("shows subscriber count and total delivered", () => {
    const { container } = render(
      <EventBusCard subscriptions={subs} recentEvents={[]} appName="App" />,
    );
    expect(container.textContent).toContain("2 subscribers");
    expect(container.textContent).toContain("650 delivered");
  });

  it("renders subscription ids", () => {
    const { container } = render(
      <EventBusCard subscriptions={subs} recentEvents={[]} appName="App" />,
    );
    expect(container.textContent).toContain("sub-webhook");
    expect(container.textContent).toContain("sub-all");
  });

  it("shows type count for filtered subs", () => {
    const { container } = render(
      <EventBusCard subscriptions={subs} recentEvents={[]} appName="App" />,
    );
    expect(container.textContent).toContain("2 types");
  });

  it("shows wildcard label", () => {
    const { container } = render(
      <EventBusCard subscriptions={subs} recentEvents={[]} appName="App" />,
    );
    expect(container.textContent).toContain("wildcard");
  });

  it("renders recent events", () => {
    const { container } = render(
      <EventBusCard subscriptions={[]} recentEvents={events} appName="App" />,
    );
    expect(container.textContent).toContain("user.created");
    expect(container.textContent).toContain("order.placed");
  });

  it("shows empty state", () => {
    const { container } = render(
      <EventBusCard subscriptions={[]} recentEvents={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No event activity");
  });
});
