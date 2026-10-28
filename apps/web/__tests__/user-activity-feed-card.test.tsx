import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UserActivityFeedCard from "../src/components/user-activity-feed-card";

const activities = [
  {
    event_id: "e1",
    user_id: "alice",
    action: "created",
    resource_type: "project",
    resource_id: "p1",
    description: "New project",
    timestamp: new Date(Date.now() - 60000).toISOString(),
  },
  {
    event_id: "e2",
    user_id: "bob",
    action: "deleted",
    resource_type: "file",
    resource_id: "f1",
    description: "",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
  },
];

describe("UserActivityFeedCard", () => {
  it("renders header", () => {
    const { container } = render(<UserActivityFeedCard activities={activities} appName="My App" />);
    expect(container.textContent).toContain("Activity Feed");
  });

  it("shows event count", () => {
    const { container } = render(<UserActivityFeedCard activities={activities} appName="App" />);
    expect(container.textContent).toContain("2 events");
  });

  it("renders user and action", () => {
    const { container } = render(<UserActivityFeedCard activities={activities} appName="App" />);
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("project/p1");
  });

  it("shows action icons", () => {
    const { container } = render(<UserActivityFeedCard activities={activities} appName="App" />);
    expect(container.textContent).toContain("➕");
    expect(container.textContent).toContain("🗑️");
  });

  it("shows description", () => {
    const { container } = render(<UserActivityFeedCard activities={activities} appName="App" />);
    expect(container.textContent).toContain("New project");
  });

  it("shows empty state", () => {
    const { container } = render(<UserActivityFeedCard activities={[]} appName="App" />);
    expect(container.textContent).toContain("No activity");
  });
});
