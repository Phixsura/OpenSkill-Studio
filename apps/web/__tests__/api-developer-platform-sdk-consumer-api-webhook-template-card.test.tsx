import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookTemplateCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-template-card";

describe("WebhookTemplateCard", () => {
  it("renders title and templates", () => {
    const { container } = render(<WebhookTemplateCard />);
    expect(container.textContent).toContain("Webhook Templates");
    expect(container.textContent).toContain("Order Created");
    expect(container.textContent).toContain("Payment Failed");
  });

  it("shows event types and count", () => {
    const { container } = render(<WebhookTemplateCard />);
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("3 templates");
  });
});
