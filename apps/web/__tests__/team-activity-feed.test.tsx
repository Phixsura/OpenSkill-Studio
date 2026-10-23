import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TeamActivityFeed } from "@/components/team-activity-feed";

describe("TeamActivityFeed", () => {
  const activities = [
    { actor: "Alice", action: "deployed", icon: "🚀", target: "v2.0", timestamp: "2026-01-03" },
    { actor: "Bob", action: "reviewed", icon: "⭐", target: "PR #42", timestamp: "2026-01-02" },
  ];
  const top = [{ name: "Alice", count: 5 }];
  it("renders feed", () => {
    const { container } = render(
      <TeamActivityFeed activities={activities} topContributors={top} uniqueMembers={2} />
    );
    expect(container.textContent).toContain("Team Activity");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("deployed");
    expect(container.textContent).toContain("2 members active");
    expect(container.textContent).toContain("5 actions");
  });
});
