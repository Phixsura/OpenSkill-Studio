import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookRoutingCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-routing-card";

describe("WebhookRoutingCard", () => {
  it("renders title and rules", () => {
    const { container } = render(<WebhookRoutingCard />);
    expect(container.textContent).toContain("Webhook Routing");
    expect(container.textContent).toContain("Orders");
    expect(container.textContent).toContain("High Value");
  });

  it("shows rule count", () => {
    const { container } = render(<WebhookRoutingCard />);
    expect(container.textContent).toContain("3 routing rules");
  });
});
