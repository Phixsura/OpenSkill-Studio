import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimelineCard } from "@/components/incident-timeline-card";

describe("IncidentTimelineCard", () => {
  it("renders incident", () => {
    const { container } = render(
      <IncidentTimelineCard title="DB Down" severity="critical" status="resolved" durationMin={10}
        events={[
          { type: "triggered", message: "Alert fired" },
          { type: "acknowledged" },
          { type: "resolved", message: "Fixed" },
        ]} />
    );
    expect(container.textContent).toContain("DB Down");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("10 min");
    expect(container.textContent).toContain("3 events");
    expect(container.textContent).toContain("triggered");
    expect(container.textContent).toContain("resolved");
  });
});
