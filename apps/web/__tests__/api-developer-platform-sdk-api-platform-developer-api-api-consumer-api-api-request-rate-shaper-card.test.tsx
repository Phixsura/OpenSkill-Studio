import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-rate-shaper-card";

describe("RequestRateShaperCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", target_rps: 50, burst_tolerance: 1.5 }];
    const { container } = render(<Card configs={configs} shapingRate={5} appName="App" />);
    expect(container.textContent).toContain("Rate Shaper");
    expect(container.textContent).toContain("50 rps");
    expect(container.textContent).toContain("1.5x burst");
    expect(container.textContent).toContain("5% shaped");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} shapingRate={0} appName="App" />);
    expect(container.textContent).toContain("No rate shaping configs");
  });
});
