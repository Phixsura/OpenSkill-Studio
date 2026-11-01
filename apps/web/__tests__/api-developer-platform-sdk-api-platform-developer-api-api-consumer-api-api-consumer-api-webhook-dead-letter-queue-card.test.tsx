import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-dead-letter-queue-card";

describe("WebhookDeadLetterQueueCard", () => {
  it("shows entries and counts", () => {
    const entries = [{ id: "e1", eventType: "order.created", error: "timeout", attempts: 5, lastFailedAt: "12:00", status: "pending" }];
    const { container } = render(<Card entries={entries} counts={{ pending: 3, requeued: 1, discarded: 2 }} appName="App" />);
    expect(container.textContent).toContain("Dead Letter Queue");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("5 attempts");
    expect(container.textContent).toContain("timeout");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} counts={{ pending: 0, requeued: 0, discarded: 0 }} appName="App" />);
    expect(container.textContent).toContain("Queue empty");
  });
});
