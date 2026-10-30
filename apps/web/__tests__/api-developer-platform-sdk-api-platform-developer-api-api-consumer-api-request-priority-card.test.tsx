import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-request-priority-card";

describe("RequestPriorityCard", () => {
  it("shows priorities", () => {
    const configs = [{ consumer_id: "c1", priority_level: 9, queue_position: "critical" }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Request Priority");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("P9");
    expect(container.textContent).toContain("critical");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No priorities configured");
  });
});
