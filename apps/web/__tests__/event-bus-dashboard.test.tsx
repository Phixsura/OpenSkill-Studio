import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventBusDashboard } from "@/components/event-bus-dashboard";

describe("EventBusDashboard", () => {
  it("renders bus", () => {
    const { container } = render(
      <EventBusDashboard topicCount={2} totalSubscriptions={3}
        topics={{ "user.created": ["send_welcome", "create_profile"], "order.placed": ["process_payment"] }}
        recentEvents={[{ topic: "user.created", deliveredTo: 2 }]} />
    );
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("2 topics");
    expect(container.textContent).toContain("3 subs");
    expect(container.textContent).toContain("user.created");
    expect(container.textContent).toContain("send_welcome");
    expect(container.textContent).toContain("process_payment");
  });
});
