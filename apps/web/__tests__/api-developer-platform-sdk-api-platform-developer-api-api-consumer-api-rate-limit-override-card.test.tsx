import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-rate-limit-override-card";

describe("RateLimitOverrideCard", () => {
  it("shows overrides", () => {
    const overrides = [{ override_id: "o1", consumer_id: "c1", endpoint: "/api", original_rpm: 60, override_rpm: 120, reason: "Launch", active: true }];
    const { container } = render(<Card overrides={overrides} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Rate Overrides");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("60→120 rpm");
  });
  it("shows empty", () => {
    const { container } = render(<Card overrides={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No overrides");
  });
});
