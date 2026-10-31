import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-request-throttle-queue-card";

describe("ConsumerApiRequestThrottleQueueCard", () => {
  it("shows queue stats", () => {
    const { container } = render(<Card consumerId="c1" queued={5} processing={3} completed={100} dropped={2} maxQueueSize={50} appName="App" />);
    expect(container.textContent).toContain("Throttle Queue");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("5/50");
  });
  it("shows empty queue", () => {
    const { container } = render(<Card consumerId="c1" queued={0} processing={0} completed={0} dropped={0} maxQueueSize={100} appName="App" />);
    expect(container.textContent).toContain("Throttle Queue");
  });
});
