import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventSourcingViewer } from "@/components/event-sourcing-viewer";

describe("EventSourcingViewer", () => {
  it("renders events", () => {
    const { container } = render(
      <EventSourcingViewer totalEvents={100} aggregates={25}
        byType={{ created: 25, updated: 60, deleted: 15 }}
        events={[
          { seq: 3, type: "updated", aggregateId: "user-1" },
          { seq: 2, type: "updated", aggregateId: "user-1" },
          { seq: 1, type: "created", aggregateId: "user-1" },
        ]} />
    );
    expect(container.textContent).toContain("Event Store");
    expect(container.textContent).toContain("100 events");
    expect(container.textContent).toContain("25 aggregates");
    expect(container.textContent).toContain("created: 25");
    expect(container.textContent).toContain("user-1");
  });
});
