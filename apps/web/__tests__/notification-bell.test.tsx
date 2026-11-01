import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationBell } from "@/components/notification-bell";

const notifs = [
  { notifId: "n1", title: "New install", body: "ext-1 installed", category: "install", read: false, actionUrl: "" },
  { notifId: "n2", title: "Update", body: "ext-2 v2.0", category: "update", read: true, actionUrl: "" },
];

describe("NotificationBell", () => {
  it("shows unread count", () => {
    const { container } = render(<NotificationBell notifications={notifs} unreadCount={1} />);
    expect(container.textContent).toContain("1");
  });
  it("opens dropdown", () => {
    const { container } = render(<NotificationBell notifications={notifs} unreadCount={1} />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("New install");
    expect(container.textContent).toContain("Notifications");
  });
});
