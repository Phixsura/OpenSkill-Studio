import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceActivityFeed } from "@/components/marketplace-activity-feed";

const mockActivities = [
  { id: "1", type: "install" as const, actor: "Acme Corp", target: "Slack Bot", message: "installed", timestamp: "2m ago" },
  { id: "2", type: "publish" as const, actor: "Alice", target: "Analytics v2.0", message: "published", timestamp: "1h ago" },
  { id: "3", type: "review" as const, actor: "Bob", target: "Dark Theme", message: "reviewed", timestamp: "3h ago" },
  { id: "4", type: "incident" as const, actor: "System", target: "API Gateway", message: "detected incident on", timestamp: "5h ago" },
];

describe("MarketplaceActivityFeed", () => {
  it("renders activities", () => {
    const { container } = render(<MarketplaceActivityFeed activities={mockActivities} />);
    expect(container.textContent).toContain("Activity Feed");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("4 events");
  });

  it("filters by type", () => {
    const { container, getByText } = render(<MarketplaceActivityFeed activities={mockActivities} />);
    fireEvent.click(getByText("incident"));
    expect(container.textContent).toContain("1 events");
    expect(container.textContent).toContain("API Gateway");
  });

  it("shows load more", () => {
    const onLoad = vi.fn();
    const { getByText } = render(
      <MarketplaceActivityFeed activities={mockActivities} hasMore onLoadMore={onLoad} />
    );
    fireEvent.click(getByText("Load more..."));
    expect(onLoad).toHaveBeenCalled();
  });
});
