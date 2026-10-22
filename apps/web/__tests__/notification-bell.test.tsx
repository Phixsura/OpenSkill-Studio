import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationBell } from "@/components/notification-bell";

describe("NotificationBell", () => {
  const notifs = [
    { type: "info", title: "New Install", message: "App installed", read: false, created_at: "" },
    { type: "info", title: "Review", message: "Got a review", read: true, created_at: "" },
  ];
  it("shows unread badge", () => {
    const { container } = render(<NotificationBell notifications={notifs} onMarkAllRead={vi.fn()} />);
    expect(container.textContent).toContain("1");
  });
  it("opens dropdown on click", () => {
    const { container } = render(<NotificationBell notifications={notifs} onMarkAllRead={vi.fn()} />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("New Install");
    expect(container.textContent).toContain("Got a review");
  });
  it("empty state", () => {
    const { container } = render(<NotificationBell notifications={[]} onMarkAllRead={vi.fn()} />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("No notifications");
  });
});
