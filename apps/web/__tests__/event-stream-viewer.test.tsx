import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventStreamViewer } from "@/components/event-stream-viewer";

describe("EventStreamViewer", () => {
  it("renders", () => {
    const { container } = render(
      <EventStreamViewer streamId="order-1" totalStreams={5}
        events={[
          { version: 1, type: "created", data: { amount: 100 } },
          { version: 2, type: "paid", data: { method: "card" } },
        ]} />
    );
    expect(container.textContent).toContain("Event Stream");
    expect(container.textContent).toContain("order-1");
    expect(container.textContent).toContain("2 events");
    expect(container.textContent).toContain("5 streams");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("paid");
  });
});
