import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookTesterCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-tester-card";

describe("WebhookTesterCard", () => {
  it("renders title and tests", () => {
    const { container } = render(<WebhookTesterCard />);
    expect(container.textContent).toContain("Webhook Tester");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("payment.failed");
  });

  it("shows pass count", () => {
    const { container } = render(<WebhookTesterCard />);
    expect(container.textContent).toContain("2/3 tests passed");
  });
});
