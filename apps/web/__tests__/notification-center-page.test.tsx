import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationCenterPage } from "@/components/notification-center-page";

describe("NotificationCenterPage", () => {
  const notifs = [
    { id: "1", title: "App installed", body: "SuperApp", icon: "📦", category: "apps", read: false, timestamp: "2026-10-01" },
  ];
  const cats = [{ id: "apps", label: "Apps", count: 1, unread: 1 }];
  it("renders notifications", () => {
    const { container } = render(
      <NotificationCenterPage notifications={notifs} unread={1} categories={cats}
        onMarkRead={vi.fn()} onMarkAllRead={vi.fn()} />
    );
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("App installed");
    expect(container.textContent).toContain("1 unread");
    expect(container.textContent).toContain("Mark all read");
    expect(container.textContent).toContain("Apps");
  });
});
