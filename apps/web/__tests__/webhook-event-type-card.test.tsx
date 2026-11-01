import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookEventTypeCard from "../src/components/webhook-event-type-card";

const eventTypes = [
  {
    event_type: "app.installed",
    description: "App installed",
    category: "lifecycle",
    emit_count: 150,
  },
  {
    event_type: "webhook.sent",
    description: "Webhook delivered",
    category: "delivery",
    emit_count: 5000,
  },
];

describe("WebhookEventTypeCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <WebhookEventTypeCard
        eventTypes={eventTypes}
        categories={["lifecycle", "delivery"]}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Event Types");
    expect(container.textContent).toContain("2 types");
    expect(container.textContent).toContain("2 categories");
  });

  it("shows event types with categories", () => {
    const { container } = render(
      <WebhookEventTypeCard eventTypes={eventTypes} categories={[]} appName="App" />,
    );
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("lifecycle");
    expect(container.textContent).toContain("webhook.sent");
  });

  it("shows emit counts", () => {
    const { container } = render(
      <WebhookEventTypeCard eventTypes={eventTypes} categories={[]} appName="App" />,
    );
    expect(container.textContent).toContain("150 emitted");
    expect(container.textContent).toContain("5000 emitted");
  });

  it("shows empty state", () => {
    const { container } = render(
      <WebhookEventTypeCard eventTypes={[]} categories={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No event types");
  });
});
