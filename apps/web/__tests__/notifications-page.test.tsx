import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationsPage } from "@/components/notifications-page";

describe("NotificationsPage", () => {
  const tabs = [{ id: "apps", label: "Apps", count: 2, unread: 1 }];
  const notifs = { apps: [
    { id: "1", title: "App installed", body: "SuperApp", icon: "📦", read: false, timestamp: "2026-01-01" },
  ]};
  it("renders notifications", () => {
    const { container } = render(
      <NotificationsPage tabs={tabs} notificationsByTab={notifs} unread={1} onMarkRead={vi.fn()} />
    );
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("1 unread");
    expect(container.textContent).toContain("App installed");
    expect(container.textContent).toContain("Apps");
  });
});
