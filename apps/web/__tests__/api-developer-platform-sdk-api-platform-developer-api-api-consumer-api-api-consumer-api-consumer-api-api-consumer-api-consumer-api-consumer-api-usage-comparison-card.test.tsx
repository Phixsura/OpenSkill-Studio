import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-usage-comparison-card";

describe("UsageComparisonCard", () => {
  it("shows comparison", () => {
    const consumers = [{ consumerId: "c1", requests: 5000, errors: 10, avgMs: 50 }, { consumerId: "c2", requests: 1000, errors: 5, avgMs: 80 }];
    const { container } = render(<Card consumers={consumers} highestUsage="c1" totalRequests={6000} avgRequests={3000} appName="App" />);
    expect(container.textContent).toContain("Usage Comparison");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("👑");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumers={[]} highestUsage="" totalRequests={0} avgRequests={0} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
