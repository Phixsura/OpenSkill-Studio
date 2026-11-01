import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationCenterV2 } from "@/components/notification-center-v2";

describe("NotificationCenterV2", () => {
  const notifs = [
    { title: "New install", icon: "📥", event_type: "install", details: {}, read: false },
    { title: "New review", icon: "⭐", event_type: "review", details: {}, read: true },
  ];
  it("renders notifications", () => {
    const { container } = render(<NotificationCenterV2 notifications={notifs} onMarkRead={vi.fn()} onClearAll={vi.fn()} />);
    expect(container.textContent).toContain("New install");
    expect(container.textContent).toContain("1"); // unread badge
  });
  it("clear all", () => {
    const fn = vi.fn();
    const { container } = render(<NotificationCenterV2 notifications={notifs} onMarkRead={vi.fn()} onClearAll={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Clear all")!);
    expect(fn).toHaveBeenCalled();
  });
  it("empty state", () => {
    const { container } = render(<NotificationCenterV2 notifications={[]} onMarkRead={vi.fn()} onClearAll={vi.fn()} />);
    expect(container.textContent).toContain("No notifications");
  });
});
