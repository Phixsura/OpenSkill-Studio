import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-batch-sender-card";

describe("WebhookBatchSenderCard", () => {
  it("shows stats", () => {
    const stats = { total: 50, pending: 5, success: 40, failed: 5, total_events: 2500 };
    const { container } = render(<Card stats={stats} appName="App" />);
    expect(container.textContent).toContain("Batch Sender");
    expect(container.textContent).toContain("5 pending");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("2,500");
  });
  it("no pending badge when zero", () => {
    const stats = { total: 0, pending: 0, success: 0, failed: 0, total_events: 0 };
    const { container } = render(<Card stats={stats} appName="App" />);
    expect(container.textContent).not.toContain("pending");
  });
});
