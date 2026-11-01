import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookBatchCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-batch-card";

describe("WebhookBatchCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<WebhookBatchCard />);
    expect(container.textContent).toContain("Webhook Batch Sender");
    expect(container.textContent).toContain("230");
    expect(container.textContent).toContain("Sent");
  });

  it("shows event count", () => {
    const { container } = render(<WebhookBatchCard />);
    expect(container.textContent).toContain("8,500 events");
    expect(container.textContent).toContain("17 buffered");
  });
});
