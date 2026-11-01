import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookInspectorCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-inspector-card";

describe("WebhookInspectorCard", () => {
  it("renders title and entries", () => {
    const { container } = render(<WebhookInspectorCard />);
    expect(container.textContent).toContain("Webhook Inspector");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("payment.failed");
  });

  it("shows status and count", () => {
    const { container } = render(<WebhookInspectorCard />);
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("3 recent inspections");
  });
});
