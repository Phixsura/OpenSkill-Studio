import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookMonitorCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-monitor-card";

describe("WebhookMonitorCard", () => {
  it("renders title and webhooks", () => {
    const { container } = render(<WebhookMonitorCard />);
    expect(container.textContent).toContain("Webhook Monitor");
    expect(container.textContent).toContain("wh-orders");
    expect(container.textContent).toContain("wh-alerts");
  });

  it("shows healthy count", () => {
    const { container } = render(<WebhookMonitorCard />);
    expect(container.textContent).toContain("1/3 healthy");
  });
});
