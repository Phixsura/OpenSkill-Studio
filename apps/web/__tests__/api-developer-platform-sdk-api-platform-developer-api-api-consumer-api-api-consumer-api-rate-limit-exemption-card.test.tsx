import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-rate-limit-exemption-card";

describe("ConsumerApiRateLimitExemptionCard", () => {
  it("shows exemptions", () => {
    const exemptions = [{ exemption_id: "e1", consumer_id: "c1", reason: "Launch", multiplier: 3, active: true, hours_remaining: 48 }];
    const { container } = render(<Card exemptions={exemptions} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Rate Exemptions");
    expect(container.textContent).toContain("Launch");
    expect(container.textContent).toContain("3×");
    expect(container.textContent).toContain("48h");
  });
  it("shows empty", () => {
    const { container } = render(<Card exemptions={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No exemptions");
  });
});
