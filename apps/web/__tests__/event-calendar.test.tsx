import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventCalendar } from "@/components/event-calendar";

describe("EventCalendar", () => {
  it("renders events", () => {
    const { container } = render(
      <EventCalendar total={2} events={[
        { title: "v4.0 Launch", date: "2026-11-01", type: "release", icon: "🚀", description: "Major release" },
        { title: "DevCon", date: "2026-12-15", type: "hackathon", icon: "💻", description: "" },
      ]} />
    );
    expect(container.textContent).toContain("Upcoming Events");
    expect(container.textContent).toContain("2 events");
    expect(container.textContent).toContain("v4.0 Launch");
    expect(container.textContent).toContain("Major release");
    expect(container.textContent).toContain("DevCon");
  });
});
