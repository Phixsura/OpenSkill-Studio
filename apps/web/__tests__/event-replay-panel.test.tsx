import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventReplayPanel } from "@/components/event-replay-panel";
describe("EventReplayPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EventReplayPanel totalEvents={100} eventTypes={5}
        events={[
          { seq: 1, type: "order.created", timestamp: 1000 },
          { seq: 2, type: "order.paid", timestamp: 1001 },
        ]} />
    );
    expect(container.textContent).toContain("Event Replay");
    expect(container.textContent).toContain("100 events");
    expect(container.textContent).toContain("5 types");
    expect(container.textContent).toContain("#1");
    expect(container.textContent).toContain("order.created");
  });
});
