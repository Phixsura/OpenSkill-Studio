import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RequestThrottleCard from "../src/components/api-developer-platform-sdk-consumer-api-request-throttle-card";

describe("RequestThrottleCard", () => {
  it("renders title and consumers", () => {
    const { container } = render(<RequestThrottleCard />);
    expect(container.textContent).toContain("Request Throttle");
    expect(container.textContent).toContain("c-acme");
    expect(container.textContent).toContain("c-beta");
  });

  it("shows backpressure info", () => {
    const { container } = render(<RequestThrottleCard />);
    expect(container.textContent).toContain("backpressure");
    expect(container.textContent).toContain("1 under backpressure");
  });
});
