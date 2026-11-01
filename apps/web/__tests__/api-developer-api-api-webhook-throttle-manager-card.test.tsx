import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookThrottleManagerCard from "../src/components/api-developer-api-api-webhook-throttle-manager-card";

const configs = [
  { destination: "https://api.example.com/hook", max_per_second: 10, max_per_minute: 100, throttled_count: 25 },
];

describe("APIDeveloperAPIApiWebhookThrottleManagerCard", () => {
  it("shows throttle configs", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookThrottleManagerCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("Webhook Throttles");
    expect(container.textContent).toContain("25 throttled");
    expect(container.textContent).toContain("10/s");
    expect(container.textContent).toContain("100/m");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookThrottleManagerCard configs={[]} appName="App" />);
    expect(container.textContent).toContain("No throttle configs");
  });
});
