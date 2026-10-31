import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-consumer-notification-dispatcher-card";

describe("NotificationDispatcherCard", () => {
  it("shows notifications", () => {
    const notifications = [{ id: "n1", title: "High Errors", message: "Error rate above 5%", severity: "warning", read: false, dispatchedAt: "12:00", channels: ["email"] }];
    const { container } = render(<Card notifications={notifications} unreadCount={1} channels={["email", "slack"]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("High Errors");
    expect(container.textContent).toContain("Error rate above 5%");
  });
  it("shows empty", () => {
    const { container } = render(<Card notifications={[]} unreadCount={0} channels={["in_app"]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No notifications");
  });
});
