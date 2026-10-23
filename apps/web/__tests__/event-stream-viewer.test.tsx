import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventStreamViewer } from "@/components/event-stream-viewer";

describe("EventStreamViewer", () => {
  it("renders events", () => {
    const { container } = render(
      <EventStreamViewer streamId="order-1" version={3} totalStreams={5} events={[
        { seq: 1, type: "created", stream: "order-1", data: { total: 100 } },
        { seq: 2, type: "paid", stream: "order-1", data: { method: "card" } },
        { seq: 3, type: "shipped", stream: "order-1", data: { tracking: "TRK123" } },
      ]} />
    );
    expect(container.textContent).toContain("Event Stream");
    expect(container.textContent).toContain("order-1");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("shipped");
    expect(container.textContent).toContain("TRK123");
  });
});
