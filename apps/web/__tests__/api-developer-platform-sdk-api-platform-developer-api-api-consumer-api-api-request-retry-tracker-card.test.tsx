import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-retry-tracker-card";

describe("RequestRetryTrackerCard", () => {
  it("shows records", () => {
    const records = [{ consumer_id: "c1", endpoint: "/api", total_attempts: 50, success_rate: 80, max_reached: 5 }];
    const { container } = render(<Card records={records} totalRetries={50} appName="App" />);
    expect(container.textContent).toContain("Retry Tracker");
    expect(container.textContent).toContain("50 total retries");
    expect(container.textContent).toContain("80% ok");
  });
  it("shows empty", () => {
    const { container } = render(<Card records={[]} totalRetries={0} appName="App" />);
    expect(container.textContent).toContain("No retry data");
  });
});
