import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPINotificationCenterCard from "../src/components/api-developer-api-notification-center-card";

const notifs = [
  { notification_id: "n1", title: "v3.0 Released", category: "changelog", read: false },
  { notification_id: "n2", title: "API Outage Resolved", category: "incident", read: true },
];

describe("APIDeveloperAPINotificationCenterCard", () => {
  it("shows notifications with badge", () => {
    const { container } = render(<APIDeveloperAPINotificationCenterCard notifications={notifs} unreadCount={1} appName="App" />);
    expect(container.textContent).toContain("Notification Center");
    expect(container.textContent).toContain("1");
    expect(container.textContent).toContain("v3.0 Released");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPINotificationCenterCard notifications={[]} unreadCount={0} appName="App" />);
    expect(container.textContent).toContain("No notifications");
  });
});
