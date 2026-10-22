import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationCenter } from "@/components/notification-center";

describe("NotificationCenter", () => {
  it("shows notifications", () => {
    const { container } = render(<NotificationCenter notifications={[{ title: "Install", message: "Done", type: "success", read: false, createdAt: "" }]} unreadCount={1} onMarkRead={vi.fn()} />);
    expect(container.textContent).toContain("Install");
  });
  it("shows unread count", () => {
    const { container } = render(<NotificationCenter notifications={[]} unreadCount={5} onMarkRead={vi.fn()} />);
    expect(container.textContent).toContain("5");
  });
  it("empty state", () => {
    const { container } = render(<NotificationCenter notifications={[]} unreadCount={0} onMarkRead={vi.fn()} />);
    expect(container.textContent).toContain("No notifications");
  });
});
