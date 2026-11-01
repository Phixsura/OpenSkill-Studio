import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CommunityLeaderboard } from "@/components/community-leaderboard";

describe("CommunityLeaderboard", () => {
  it("renders leaderboard", () => {
    const { container } = render(
      <CommunityLeaderboard period="monthly" members={[
        { name: "Alice", score: 250, rank: 1, badge: "🥇", forumPosts: 50, appsPublished: 3 },
        { name: "Bob", score: 120, rank: 2, badge: "🥈", forumPosts: 30, appsPublished: 1 },
      ]} />
    );
    expect(container.textContent).toContain("Community Leaders");
    expect(container.textContent).toContain("monthly");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("🥇");
    expect(container.textContent).toContain("250 pts");
    expect(container.textContent).toContain("Bob");
  });
});
