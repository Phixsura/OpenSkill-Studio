import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-notification-channel-card";

describe("ConsumerApiNotificationChannelCard", () => {
  it("shows channels", () => {
    const channels = [{ id: "ch1", type: "email", destination: "a@b.com", verified: true, enabled: true }];
    const { container } = render(<Card channels={channels} consumerId="c1" unreadCount={3} appName="App" />);
    expect(container.textContent).toContain("Notification Channels");
    expect(container.textContent).toContain("a@b.com");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("3");
  });
  it("shows empty", () => {
    const { container } = render(<Card channels={[]} consumerId="c1" unreadCount={0} appName="App" />);
    expect(container.textContent).toContain("No channels configured");
  });
});
