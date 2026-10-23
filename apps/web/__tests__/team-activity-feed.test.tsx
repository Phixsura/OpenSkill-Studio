import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamActivityFeed } from "@/components/team-activity-feed";

describe("TeamActivityFeed", () => {
  const activities = [
    { id: "a1", actor: "Alice", action: "published", target: "SDK v2", type: "release", timestamp: "2026-10-23T11:00:00" },
    { id: "a2", actor: "Bob", action: "merged", target: "PR #42", type: "code", timestamp: "2026-10-23T09:00:00" },
  ];
  it("renders", () => {
    const { container } = render(
      <TeamActivityFeed activities={activities} hasMore={false} onLoadMore={vi.fn()} />
    );
    expect(container.textContent).toContain("Team Activity");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("published");
    expect(container.textContent).toContain("🚀");
  });
  it("load more", () => {
    const fn = vi.fn();
    const { container } = render(
      <TeamActivityFeed activities={activities} hasMore={true} onLoadMore={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Load More")!);
    expect(fn).toHaveBeenCalled();
  });
});
