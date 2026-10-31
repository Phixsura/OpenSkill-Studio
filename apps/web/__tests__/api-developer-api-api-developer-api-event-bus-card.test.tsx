import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiEventBusCard from "../src/components/api-developer-api-api-developer-api-event-bus-card";

const subs = [
  { subscription_id: "s1", event_pattern: "user.*", handler_url: "https://api.example.com/hooks", events_received: 1500 },
  { subscription_id: "s2", event_pattern: "order.created", handler_url: "https://billing.example.com/hooks", events_received: 800 },
];

describe("APIDeveloperAPIApiDeveloperApiEventBusCard", () => {
  it("shows event bus", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiEventBusCard subscriptions={subs} recentEventCount={5000} appName="App" />);
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("5000 events");
    expect(container.textContent).toContain("user.*");
    expect(container.textContent).toContain("1500");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiEventBusCard subscriptions={[]} recentEventCount={0} appName="App" />);
    expect(container.textContent).toContain("No subscriptions");
  });
});
