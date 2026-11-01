import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-queue-priority-card";

describe("RequestQueuePriorityCard", () => {
  it("shows queue info", () => {
    const { container } = render(<Card depth={250} maxQueue={5000} nextPriority={1} appName="App" />);
    expect(container.textContent).toContain("Priority Queue");
    expect(container.textContent).toContain("250/5000");
    expect(container.textContent).toContain("P1 next");
  });
  it("shows empty", () => {
    const { container } = render(<Card depth={0} maxQueue={1000} nextPriority={null} appName="App" />);
    expect(container.textContent).toContain("0/1000");
  });
});
