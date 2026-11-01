import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiRequestThrottleCard from "../src/components/api-developer-api-api-developer-api-api-request-throttle-card";

const states = [
  { consumer_id: "acme", base_rate: 100, current_rate: 50, backoff_factor: 2, throttled_count: 3 },
  { consumer_id: "beta", base_rate: 50, current_rate: 50, backoff_factor: 1, throttled_count: 0 },
];

describe("APIDeveloperAPIApiDeveloperApiApiRequestThrottleCard", () => {
  it("shows throttle states", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiRequestThrottleCard states={states} throttledCount={1} appName="App" />);
    expect(container.textContent).toContain("Request Throttle");
    expect(container.textContent).toContain("1 throttled");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("50/100 rps");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiRequestThrottleCard states={[]} throttledCount={0} appName="App" />);
    expect(container.textContent).toContain("No throttle configs");
  });
});
