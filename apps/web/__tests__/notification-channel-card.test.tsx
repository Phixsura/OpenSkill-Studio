import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import NotificationChannelCard from "../src/components/notification-channel-card";

const channels = [
  {
    channel_id: "ch1",
    channel_type: "slack",
    name: "Dev Alerts",
    enabled: true,
    test_success: true,
    success_rate: 99.5,
  },
  {
    channel_id: "ch2",
    channel_type: "email",
    name: "Admin Email",
    enabled: false,
    test_success: null,
    success_rate: 100,
  },
];

describe("NotificationChannelCard", () => {
  it("renders header and enabled count", () => {
    const { container } = render(<NotificationChannelCard channels={channels} appName="App" />);
    expect(container.textContent).toContain("Notification Channels");
    expect(container.textContent).toContain("1/2 enabled");
  });

  it("shows channel names and types", () => {
    const { container } = render(<NotificationChannelCard channels={channels} appName="App" />);
    expect(container.textContent).toContain("Dev Alerts");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("email");
  });

  it("shows success rate", () => {
    const { container } = render(<NotificationChannelCard channels={channels} appName="App" />);
    expect(container.textContent).toContain("99.5%");
  });

  it("shows empty state", () => {
    const { container } = render(<NotificationChannelCard channels={[]} appName="App" />);
    expect(container.textContent).toContain("No channels configured");
  });
});
