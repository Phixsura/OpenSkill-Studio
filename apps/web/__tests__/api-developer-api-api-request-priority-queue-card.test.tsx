import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiRequestPriorityQueueCard from "../src/components/api-developer-api-api-request-priority-queue-card";

describe("APIDeveloperAPIApiRequestPriorityQueueCard", () => {
  it("shows priority queue", () => {
    const { container } = render(<APIDeveloperAPIApiRequestPriorityQueueCard queueSize={25} distribution={{ critical: 2, high: 8, normal: 10, low: 5 }} appName="App" />);
    expect(container.textContent).toContain("Priority Queue");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("high");
  });
});
