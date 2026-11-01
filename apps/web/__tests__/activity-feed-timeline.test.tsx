import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActivityFeedTimeline } from "@/components/activity-feed-timeline";

describe("ActivityFeedTimeline", () => {
  it("renders feed", () => {
    const { container } = render(
      <ActivityFeedTimeline count={3} byAction={{ deployed: 1, reviewed: 1, created: 1 }}
        items={[
          { actor: "alice", action: "created", target: "webhook-config" },
          { actor: "bob", action: "reviewed", target: "PR #42" },
          { actor: "alice", action: "deployed", target: "api-v2" },
        ]} />
    );
    expect(container.textContent).toContain("Activity Feed");
    expect(container.textContent).toContain("3 activities");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("webhook-config");
    expect(container.textContent).toContain("bob");
  });
});
