import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ActivityFeed } from "@/components/activity-feed";

describe("ActivityFeed", () => {
  const activities = [
    { id: "1", actor: "Alice", verb: "installed", target: "MyApp", icon: "📦", timestamp: "2026-01-02T00:00:00Z" },
    { id: "2", actor: "Bob", verb: "reviewed", target: "MyApp", icon: "⭐", timestamp: "2026-01-01T00:00:00Z" },
  ];
  it("renders activities", () => {
    const { container } = render(<ActivityFeed activities={activities} hasMore={false} onLoadMore={vi.fn()} />);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("installed");
    expect(container.textContent).toContain("MyApp");
  });
  it("load more", () => {
    const fn = vi.fn();
    const { container } = render(<ActivityFeed activities={activities} hasMore={true} onLoadMore={fn} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Load more")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalled();
  });
});
