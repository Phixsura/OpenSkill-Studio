import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationHubPanel } from "@/components/notification-hub-panel";

const mockNotifs = [
  { notificationId: "n1", title: "Deployed v2.0", body: "Slack Bot deployed",
    channels: ["in_app", "email"], read: false, timestamp: "5m ago" },
  { notificationId: "n2", title: "New review", body: "4 stars",
    channels: ["in_app"], read: true, timestamp: "1h ago" },
];

describe("NotificationHubPanel", () => {
  it("renders notifications", () => {
    const { container } = render(<NotificationHubPanel notifications={mockNotifs} unreadCount={1} />);
    expect(container.textContent).toContain("Deployed v2.0");
    expect(container.textContent).toContain("1");
  });

  it("calls onMarkAllRead", () => {
    const fn = vi.fn();
    const { getByText } = render(<NotificationHubPanel notifications={mockNotifs} unreadCount={1} onMarkAllRead={fn} />);
    fireEvent.click(getByText("Mark all read"));
    expect(fn).toHaveBeenCalled();
  });
});
