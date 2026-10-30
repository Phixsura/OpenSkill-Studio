import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-webhook-template-card";

describe("ConsumerWebhookTemplateCard", () => {
  it("shows templates", () => {
    const templates = [{ id: "t1", name: "Order Notification", contentType: "application/json", variableCount: 3 }];
    const { container } = render(<Card templates={templates} appName="App" />);
    expect(container.textContent).toContain("Webhook Templates");
    expect(container.textContent).toContain("Order Notification");
    expect(container.textContent).toContain("3 vars");
  });
  it("shows empty", () => {
    const { container } = render(<Card templates={[]} appName="App" />);
    expect(container.textContent).toContain("No templates");
  });
});
