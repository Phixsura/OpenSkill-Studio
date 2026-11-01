import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-request-throttle-card";

describe("RequestThrottleCard", () => {
  it("shows throttle info", () => {
    const consumers = [{ consumer_id: "c1", active: 3, max_concurrent: 10, throttle_rate: 5.2, total_throttled: 15 }];
    const { container } = render(<Card consumers={consumers} appName="App" />);
    expect(container.textContent).toContain("Request Throttle");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("3/10 active");
    expect(container.textContent).toContain("5.2% throttled");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumers={[]} appName="App" />);
    expect(container.textContent).toContain("No throttle configs");
  });
});
