import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogNotificationCard from "../src/components/api-changelog-notification-card";

const notifs = [{ notification_id: "n1", version: "v2.0", channel: "email", recipient_count: 100, delivered: 98, failed: 2 }];

describe("APIChangelogNotificationCard", () => {
  it("shows notifications", () => {
    const { container } = render(<APIChangelogNotificationCard notifications={notifs} appName="App" />);
    expect(container.textContent).toContain("Changelog Notifications");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("98/100 delivered");
  });
  it("shows empty", () => {
    const { container } = render(<APIChangelogNotificationCard notifications={[]} appName="App" />);
    expect(container.textContent).toContain("No notifications sent");
  });
});
