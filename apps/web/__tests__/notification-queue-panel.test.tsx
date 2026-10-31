import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationQueuePanel } from "@/components/notification-queue-panel";

const mockNotifications = [
  { notificationId: "n1", title: "Deploy Complete", message: "v1.0 deployed",
    priority: "high" as const, category: "deploy", read: false, createdAt: "5m ago" },
  { notificationId: "n2", title: "Low disk", message: "90% used",
    priority: "urgent" as const, category: "alert", read: false, createdAt: "10m ago" },
  { notificationId: "n3", title: "Update available", message: "v2.0",
    priority: "low" as const, category: "info", read: true, createdAt: "1h ago" },
];

describe("NotificationQueuePanel", () => {
  it("renders unread notifications", () => {
    const { container } = render(
      <NotificationQueuePanel notifications={mockNotifications} unreadCount={2} />
    );
    expect(container.textContent).toContain("Deploy Complete");
    expect(container.textContent).toContain("Low disk");
  });

  it("shows unread count badge", () => {
    const { container } = render(
      <NotificationQueuePanel notifications={mockNotifications} unreadCount={2} />
    );
    expect(container.textContent).toContain("2");
  });

  it("calls onMarkRead", () => {
    const onMarkRead = vi.fn();
    const { getAllByText } = render(
      <NotificationQueuePanel notifications={mockNotifications} unreadCount={2} onMarkRead={onMarkRead} />
    );
    fireEvent.click(getAllByText("Read")[0]);
    expect(onMarkRead).toHaveBeenCalledWith("n1");
  });

  it("calls onMarkAllRead", () => {
    const onMarkAllRead = vi.fn();
    const { getByText } = render(
      <NotificationQueuePanel notifications={mockNotifications} unreadCount={2} onMarkAllRead={onMarkAllRead} />
    );
    fireEvent.click(getByText("Mark All Read"));
    expect(onMarkAllRead).toHaveBeenCalled();
  });
});
