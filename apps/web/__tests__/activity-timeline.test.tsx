import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActivityTimeline } from "@/components/activity-timeline";

describe("ActivityTimeline", () => {
  const activities = [
    { user_id: "alice", action: "install", resource: "app_1", timestamp: "2026-10-23T12:00:00" },
    { user_id: "bob", action: "view", resource: "app_2", timestamp: "2026-10-23T11:00:00" },
  ];
  it("renders", () => {
    const { container } = render(
      <ActivityTimeline activities={activities} totalActivities={2} uniqueUsers={2} />
    );
    expect(container.textContent).toContain("Activity Timeline");
    expect(container.textContent).toContain("2 actions");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("install");
    expect(container.textContent).toContain("bob");
  });
});
