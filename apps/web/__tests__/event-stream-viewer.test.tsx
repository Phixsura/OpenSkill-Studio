import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventStreamViewer } from "@/components/event-stream-viewer";

describe("EventStreamViewer", () => {
  const events = [
    { event_id: "e1", type: "app.installed", source: "web", timestamp: "2026-10-23T12:00:00", payload: {} },
    { event_id: "e2", type: "review.created", source: "api", timestamp: "2026-10-23T11:00:00", payload: {} },
  ];
  it("renders", () => {
    const { container } = render(<EventStreamViewer events={events} hasMore={false} onLoadMore={vi.fn()} />);
    expect(container.textContent).toContain("Event Stream");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("📥");
    expect(container.textContent).toContain("review.created");
  });
});
