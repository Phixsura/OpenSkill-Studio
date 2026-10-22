import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActivityFeed } from "@/components/activity-feed";

const ACTIVITIES = [
  { action: "create_app", resource: "app/my-app", details: "", timestamp: "2min ago" },
  { action: "publish", resource: "app/my-app v2.0", details: "Published to marketplace", timestamp: "5min ago" },
];

describe("ActivityFeed", () => {
  it("shows activities", () => {
    const { container } = render(<ActivityFeed activities={ACTIVITIES} />);
    expect(container.textContent).toContain("create app");
    expect(container.textContent).toContain("publish");
  });

  it("shows icons", () => {
    const { container } = render(<ActivityFeed activities={ACTIVITIES} />);
    expect(container.textContent).toContain("📦");
  });

  it("empty state", () => {
    const { container } = render(<ActivityFeed activities={[]} />);
    expect(container.textContent).toContain("No recent");
  });

  it("shows timestamp", () => {
    const { container } = render(<ActivityFeed activities={ACTIVITIES} />);
    expect(container.textContent).toContain("2min ago");
  });
});
