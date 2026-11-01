import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import NotificationRouterCard from "../src/components/notification-router-card";

const webhookChannel = {
  channel_id: "ch-1",
  channel_type: "webhook" as const,
  target: "https://example.com/webhook",
  event_types: ["app.installed", "app.error"],
  enabled: true,
  delivery_count: 42,
  last_delivery_status: "delivered" as const,
};

const slackChannel = {
  channel_id: "ch-2",
  channel_type: "slack" as const,
  target: "#app-alerts",
  event_types: null,
  enabled: true,
  delivery_count: 100,
  last_delivery_status: "delivered" as const,
};

const disabledChannel = {
  channel_id: "ch-3",
  channel_type: "email" as const,
  target: "admin@example.com",
  event_types: ["app.error"],
  enabled: false,
  delivery_count: 5,
  last_delivery_status: "skipped" as const,
};

const failedChannel = {
  channel_id: "ch-4",
  channel_type: "in_app" as const,
  target: "user-dashboard",
  event_types: null,
  enabled: true,
  delivery_count: 10,
  last_delivery_status: "failed" as const,
};

describe("NotificationRouterCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <NotificationRouterCard channels={[webhookChannel]} appName="My App" />,
    );
    expect(container.textContent).toContain("Notification Channels");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(
      <NotificationRouterCard channels={[webhookChannel, slackChannel]} appName="App" />,
    );
    expect(container.textContent).toContain("2 active");
  });

  it("shows disabled count", () => {
    const { container } = render(
      <NotificationRouterCard channels={[webhookChannel, disabledChannel]} appName="App" />,
    );
    expect(container.textContent).toContain("1 disabled");
  });

  it("renders channel type labels and icons", () => {
    const { container } = render(
      <NotificationRouterCard channels={[webhookChannel, slackChannel]} appName="App" />,
    );
    expect(container.textContent).toContain("Webhook");
    expect(container.textContent).toContain("🔗");
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("💬");
  });

  it("shows target", () => {
    const { container } = render(
      <NotificationRouterCard channels={[webhookChannel]} appName="App" />,
    );
    expect(container.textContent).toContain("https://example.com/webhook");
  });

  it("shows event type count for filtered channels", () => {
    const { container } = render(
      <NotificationRouterCard channels={[webhookChannel]} appName="App" />,
    );
    expect(container.textContent).toContain("2 event types");
  });

  it("shows all events for unfiltered channels", () => {
    const { container } = render(
      <NotificationRouterCard channels={[slackChannel]} appName="App" />,
    );
    expect(container.textContent).toContain("All events");
  });

  it("shows delivery count", () => {
    const { container } = render(
      <NotificationRouterCard channels={[webhookChannel]} appName="App" />,
    );
    expect(container.textContent).toContain("42 deliveries");
  });

  it("shows delivery status", () => {
    const { container } = render(
      <NotificationRouterCard channels={[webhookChannel, failedChannel]} appName="App" />,
    );
    expect(container.textContent).toContain("Delivered");
    expect(container.textContent).toContain("Failed");
  });

  it("shows empty state", () => {
    const { container } = render(<NotificationRouterCard channels={[]} appName="App" />);
    expect(container.textContent).toContain("No channels configured");
  });
});
