import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperNotificationCard from "../src/components/api-developer-notification-card";

const notifs = [
  { notification_id: "n1", title: "API Update", channel: "in_app", read: false },
  { notification_id: "n2", title: "Maintenance", channel: "email", read: true },
];

describe("APIDeveloperNotificationCard", () => {
  it("shows notifications", () => {
    const { container } = render(<APIDeveloperNotificationCard notifications={notifs} unreadCount={1} appName="App" />);
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("1 unread");
    expect(container.textContent).toContain("API Update");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperNotificationCard notifications={[]} unreadCount={0} appName="App" />);
    expect(container.textContent).toContain("No notifications");
  });
});
