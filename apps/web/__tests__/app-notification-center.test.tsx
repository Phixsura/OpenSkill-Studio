import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppNotificationCenter } from "@/components/app-notification-center";

const MOCK_NOTIFICATIONS = [
  {
    notification_id: "n1",
    app_name: "LMS Sync",
    app_id: "app-1",
    title: "Sync complete",
    body: "42 records synced",
    priority: "info" as const,
    action_url: null,
    read: true,
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    notification_id: "n2",
    app_name: "AI Grader",
    app_id: "app-2",
    title: "Grading failed",
    body: "3 submissions could not be graded",
    priority: "warning" as const,
    action_url: "https://example.com/fix",
    read: false,
    created_at: new Date(Date.now() - 300000).toISOString(),
  },
  {
    notification_id: "n3",
    app_name: "Auth App",
    app_id: "app-3",
    title: "Action needed",
    body: "Review permission change request",
    priority: "action_required" as const,
    action_url: "https://example.com/review",
    read: false,
    created_at: new Date(Date.now() - 60000).toISOString(),
  },
];

const defaultProps = {
  notifications: MOCK_NOTIFICATIONS,
  unreadCount: 2,
  onMarkRead: vi.fn(),
  onDismiss: vi.fn(),
  onMarkAllRead: vi.fn(),
  onAction: vi.fn(),
};

describe("AppNotificationCenter", () => {
  it("renders heading", () => {
    const { container } = render(<AppNotificationCenter {...defaultProps} />);
    expect(container.textContent).toContain("Notifications");
  });

  it("renders unread badge", () => {
    const { container } = render(<AppNotificationCenter {...defaultProps} />);
    expect(container.textContent).toContain("2");
  });

  it("hides badge when no unread", () => {
    const { container } = render(<AppNotificationCenter {...defaultProps} unreadCount={0} />);
    // Badge is the round counter next to "Notifications" heading — not the priority dots
    const heading = container.querySelector("h3");
    const badge = heading?.parentElement?.querySelector(".rounded-full.bg-red-500");
    expect(badge).toBeFalsy();
  });

  it("renders notification titles", () => {
    const { container } = render(<AppNotificationCenter {...defaultProps} />);
    expect(container.textContent).toContain("Sync complete");
    expect(container.textContent).toContain("Grading failed");
    expect(container.textContent).toContain("Action needed");
  });

  it("renders app names", () => {
    const { container } = render(<AppNotificationCenter {...defaultProps} />);
    expect(container.textContent).toContain("LMS Sync");
    expect(container.textContent).toContain("AI Grader");
  });

  it("renders relative time", () => {
    const { container } = render(<AppNotificationCenter {...defaultProps} />);
    expect(container.textContent).toMatch(/\d+[mhd] ago/);
  });

  it("shows View Details for action_url notifications", () => {
    const { container } = render(<AppNotificationCenter {...defaultProps} />);
    const links = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "View Details",
    );
    expect(links.length).toBe(2); // n2 and n3 have action_url
  });

  it("calls onAction when View Details clicked", () => {
    const onAction = vi.fn();
    const { container } = render(<AppNotificationCenter {...defaultProps} onAction={onAction} />);
    const link = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "View Details",
    );
    fireEvent.click(link!);
    expect(onAction).toHaveBeenCalledWith(expect.stringContaining("https://"));
  });

  it("calls onMarkRead", () => {
    const onMarkRead = vi.fn();
    const { container } = render(
      <AppNotificationCenter {...defaultProps} onMarkRead={onMarkRead} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Mark read",
    );
    fireEvent.click(btn!);
    expect(onMarkRead).toHaveBeenCalled();
  });

  it("hides Mark read for already-read notifications", () => {
    const allRead = MOCK_NOTIFICATIONS.map((n) => ({ ...n, read: true }));
    const { container } = render(
      <AppNotificationCenter {...defaultProps} notifications={allRead} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Mark read",
    );
    expect(btn).toBeFalsy();
  });

  it("calls onDismiss", () => {
    const onDismiss = vi.fn();
    const { container } = render(<AppNotificationCenter {...defaultProps} onDismiss={onDismiss} />);
    const btns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Dismiss",
    );
    fireEvent.click(btns[0]);
    expect(onDismiss).toHaveBeenCalled();
  });

  it("calls onMarkAllRead", () => {
    const onMarkAllRead = vi.fn();
    const { container } = render(
      <AppNotificationCenter {...defaultProps} onMarkAllRead={onMarkAllRead} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Mark all read",
    );
    fireEvent.click(btn!);
    expect(onMarkAllRead).toHaveBeenCalledOnce();
  });

  it("filters to unread only", () => {
    const { container } = render(<AppNotificationCenter {...defaultProps} />);
    const unreadBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Unread",
    );
    fireEvent.click(unreadBtn!);
    // Should only show the 2 unread
    expect(container.textContent).toContain("Grading failed");
    expect(container.textContent).toContain("Action needed");
    expect(container.textContent).not.toContain("Sync complete");
  });

  it("shows empty state", () => {
    const { container } = render(
      <AppNotificationCenter {...defaultProps} notifications={[]} unreadCount={0} />,
    );
    expect(container.textContent).toContain("No notifications");
  });

  it("shows unread empty state", () => {
    const allRead = MOCK_NOTIFICATIONS.map((n) => ({ ...n, read: true }));
    const { container } = render(
      <AppNotificationCenter {...defaultProps} notifications={allRead} unreadCount={0} />,
    );
    const unreadBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Unread",
    );
    fireEvent.click(unreadBtn!);
    expect(container.textContent).toContain("No unread notifications");
  });
});
