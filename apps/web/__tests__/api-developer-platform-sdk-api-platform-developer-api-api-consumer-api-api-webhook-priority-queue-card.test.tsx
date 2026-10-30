import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-priority-queue-card";

describe("WebhookPriorityQueueCard", () => {
  it("shows queue info", () => {
    const { container } = render(<Card depth={500} maxSize={10000} enqueued={5000} dequeued={4500} nextPriority={1} appName="App" />);
    expect(container.textContent).toContain("Priority Queue");
    expect(container.textContent).toContain("500/10000");
    expect(container.textContent).toContain("P1 next");
    expect(container.textContent).toContain("5,000");
  });
  it("shows empty queue", () => {
    const { container } = render(<Card depth={0} maxSize={1000} enqueued={0} dequeued={0} nextPriority={null} appName="App" />);
    expect(container.textContent).toContain("0/1000");
  });
});
