import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventStreamViewer } from "@/components/event-stream-viewer";

describe("EventStreamViewer", () => {
  it("renders events", () => {
    const events = [
      { event_type: "created", version: 1, timestamp: "2026-01-01", data: {} },
      { event_type: "updated", version: 2, timestamp: "2026-06-01", data: {} },
    ];
    const { container } = render(<EventStreamViewer events={events} streamId="app-1" />);
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("2 events");
  });
  it("empty state", () => {
    const { container } = render(<EventStreamViewer events={[]} streamId="x" />);
    expect(container.textContent).toContain("No events");
  });
});
