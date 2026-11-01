import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventTimelineFeed } from "@/components/event-timeline-feed";

describe("EventTimelineFeed", () => {
  it("renders feed", () => {
    const { container } = render(
      <EventTimelineFeed total={2} items={[
        { id: "1", type: "deployed", title: "v2.0 deployed", description: "Production deploy",
          timestamp: "2026-10-24T12:00:00Z", actor: "bob", icon: "🚀" },
        { id: "2", type: "created", title: "App created", description: "",
          timestamp: "2026-10-24T10:00:00Z", actor: "alice", icon: "✨" },
      ]} />
    );
    expect(container.textContent).toContain("Activity Timeline");
    expect(container.textContent).toContain("2 events");
    expect(container.textContent).toContain("v2.0 deployed");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("App created");
  });
});
