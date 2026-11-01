import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookFanOutCard from "../src/components/api-webhook-fan-out-card";

const results = [{ event_type: "push", destination_count: 3, delivered: 2, failed: 1, success_rate: 66.7 }];

describe("APIWebhookFanOutCard", () => {
  it("shows fan-out results", () => {
    const { container } = render(<APIWebhookFanOutCard results={results} totalFanOuts={10} appName="App" />);
    expect(container.textContent).toContain("Webhook Fan Out");
    expect(container.textContent).toContain("push → 3 dest");
    expect(container.textContent).toContain("66.7%");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookFanOutCard results={[]} totalFanOuts={0} appName="App" />);
    expect(container.textContent).toContain("No fan-out events");
  });
});
