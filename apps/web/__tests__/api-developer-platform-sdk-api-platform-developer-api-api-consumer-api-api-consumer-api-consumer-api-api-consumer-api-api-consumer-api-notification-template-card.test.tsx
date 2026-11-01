import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-notification-template-card";

describe("ConsumerApiNotificationTemplateCard", () => {
  it("shows templates", () => {
    const templates = [{ id: "t1", name: "Welcome Email", channel: "email", variableCount: 3 }];
    const { container } = render(<Card templates={templates} appName="App" />);
    expect(container.textContent).toContain("Notification Templates");
    expect(container.textContent).toContain("Welcome Email");
    expect(container.textContent).toContain("3 vars");
  });
  it("shows empty", () => {
    const { container } = render(<Card templates={[]} appName="App" />);
    expect(container.textContent).toContain("No templates");
  });
});
