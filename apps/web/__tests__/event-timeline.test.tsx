import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventTimeline } from "@/components/event-timeline";

describe("EventTimeline", () => {
  it("renders events", () => {
    const events = [
      { type: "install", icon: "📥", title: "Installed", description: "By Acme", timestamp: "2026-01-01T00:00:00Z", actor: "admin" },
      { type: "review", icon: "⭐", title: "Review", description: "5 stars", timestamp: "2026-01-02T00:00:00Z" },
    ];
    const { container } = render(<EventTimeline events={events} />);
    expect(container.textContent).toContain("Installed");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("📥");
  });
  it("empty state", () => {
    const { container } = render(<EventTimeline events={[]} />);
    expect(container.textContent).toContain("No activity");
  });
});
