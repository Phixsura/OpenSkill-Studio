import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationInbox } from "@/components/notification-inbox";

describe("NotificationInbox", () => {
  const notifications = [
    { notification_id: "n1", title: "Deploy done", message: "v2.0 live", type: "success",
      icon: "✅", read: false, created_at: "2026-10-23T12:00:00" },
    { notification_id: "n2", title: "Old news", message: "Info", type: "info",
      icon: "ℹ️", read: true, created_at: "2026-10-22T10:00:00" },
  ];
  it("renders", () => {
    const { container } = render(
      <NotificationInbox notifications={notifications} unreadCount={1} onRead={vi.fn()} onReadAll={vi.fn()} />
    );
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("Deploy done");
    expect(container.textContent).toContain("Mark all read");
  });
  it("read", () => {
    const fn = vi.fn();
    const { container } = render(
      <NotificationInbox notifications={notifications} unreadCount={1} onRead={fn} onReadAll={vi.fn()} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]); // first notification button (after Mark all read)
    expect(fn).toHaveBeenCalledWith("n1");
  });
});
