import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ActivityFeedPanel } from "@/components/activity-feed-panel";

const mockEvents = [
  { eventId: "a1", extensionId: "ext-1", eventType: "install", actor: "alice",
    message: "Installed Slack Bot", timestamp: "5m ago" },
  { eventId: "a2", extensionId: "ext-1", eventType: "deploy", actor: "admin",
    message: "Deployed v2.0", timestamp: "10m ago" },
];

describe("ActivityFeedPanel", () => {
  it("renders events", () => {
    const { container } = render(<ActivityFeedPanel events={mockEvents} />);
    expect(container.textContent).toContain("Installed Slack Bot");
    expect(container.textContent).toContain("Deployed v2.0");
  });

  it("shows type filter buttons", () => {
    const onFilter = vi.fn();
    const { getByText } = render(<ActivityFeedPanel events={mockEvents} onFilter={onFilter} />);
    fireEvent.click(getByText("All"));
    expect(onFilter).toHaveBeenCalledWith(null);
  });
});
