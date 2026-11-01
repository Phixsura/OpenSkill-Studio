import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventLogTable } from "@/components/event-log-table";

describe("EventLogTable", () => {
  it("renders events", () => {
    const { container } = render(
      <EventLogTable countByType={{ "app.installed": 2, "user.created": 1 }}
        events={[
          { id: "evt_abc", type: "app.installed", source: "marketplace", actor: "alice" },
          { id: "evt_def", type: "user.created", source: "auth", actor: "" },
        ]} />
    );
    expect(container.textContent).toContain("Event Log");
    expect(container.textContent).toContain("app.installed: 2");
    expect(container.textContent).toContain("evt_abc");
    expect(container.textContent).toContain("marketplace");
    expect(container.textContent).toContain("alice");
  });
});
