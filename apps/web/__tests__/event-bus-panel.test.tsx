import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventBusPanel } from "@/components/event-bus-panel";

describe("EventBusPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EventBusPanel published={10000} delivered={25000}
        eventTypes={[
          { eventType: "order.created", subscribers: 3 },
          { eventType: "user.signup", subscribers: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("10,000 pub");
    expect(container.textContent).toContain("25,000 delivered");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("3 subs");
  });
});
