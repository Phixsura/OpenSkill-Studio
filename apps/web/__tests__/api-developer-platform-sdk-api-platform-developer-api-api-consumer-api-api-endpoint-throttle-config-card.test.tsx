import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-throttle-config-card";

describe("EndpointThrottleConfigCard", () => {
  it("shows configs", () => {
    const configs = [{ endpoint: "/api", method: "GET", max_rps: 100, burst_size: 20, throttle_action: "reject", throttle_rate: 5.5 }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Throttle Config");
    expect(container.textContent).toContain("100 rps");
    expect(container.textContent).toContain("reject");
    expect(container.textContent).toContain("5.5% throttled");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No throttle configs");
  });
});
