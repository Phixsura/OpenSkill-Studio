import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKWebhookConsumerNotificationChannelCard from "../src/components/api-developer-platform-sdk-webhook-consumer-notification-channel-card";

const channels = [{ channel_id: "ch1", consumer_id: "acme", channel_type: "slack", target: "#alerts", enabled: true, notifications_sent: 500 }];

describe("Card", () => {
  it("shows channels", () => {
    const { container } = render(<APIDeveloperPlatformSDKWebhookConsumerNotificationChannelCard channels={channels} appName="App" />);
    expect(container.textContent).toContain("Notification Channels");
    expect(container.textContent).toContain("1/1 active");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("500 sent");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKWebhookConsumerNotificationChannelCard channels={[]} appName="App" />);
    expect(container.textContent).toContain("No channels");
  });
});
