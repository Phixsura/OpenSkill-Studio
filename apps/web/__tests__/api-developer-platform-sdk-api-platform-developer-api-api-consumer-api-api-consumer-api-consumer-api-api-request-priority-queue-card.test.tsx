import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-request-priority-queue-card";

describe("ConsumerApiRequestPriorityQueueCard", () => {
  it("shows queue stats", () => {
    const { container } = render(<Card queueSize={25} maxSize={100} processedCount={5000} topPriority={10} appName="App" />);
    expect(container.textContent).toContain("Priority Queue");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("25/100");
    expect(container.textContent).toContain("10");
  });
  it("shows empty queue", () => {
    const { container } = render(<Card queueSize={0} maxSize={1000} processedCount={0} topPriority={null} appName="App" />);
    expect(container.textContent).toContain("0/1,000");
  });
});
