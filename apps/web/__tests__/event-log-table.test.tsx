import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventLogTable } from "@/components/event-log-table";

const ENTRIES = [{ eventId: "e1", eventType: "app.installed", status: "delivered", timestamp: "10:00", display: "app.installed → org-123" }];

describe("EventLogTable", () => {
  it("shows entries", () => {
    const { container } = render(<EventLogTable entries={ENTRIES} />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("delivered");
  });
  it("empty state", () => {
    const { container } = render(<EventLogTable entries={[]} />);
    expect(container.textContent).toContain("No events");
  });
});
