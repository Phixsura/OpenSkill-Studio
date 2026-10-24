import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventBusMonitor } from "@/components/event-bus-monitor";

describe("EventBusMonitor", () => {
  it("renders bus", () => {
    const { container } = render(
      <EventBusMonitor totalSubscribers={5} published={100} delivered={350}
        topics={[
          { topic: "user.created", subscribers: 3 },
          { topic: "order.placed", subscribers: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("350");
    expect(container.textContent).toContain("user.created");
    expect(container.textContent).toContain("3 subs");
  });
});
