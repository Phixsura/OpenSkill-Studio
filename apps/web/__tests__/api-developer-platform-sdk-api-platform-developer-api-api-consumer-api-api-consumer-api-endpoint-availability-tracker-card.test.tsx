import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-availability-tracker-card";

describe("EndpointAvailabilityTrackerCard", () => {
  it("shows availability", () => {
    const windows = [{ endpoint: "/api", method: "GET", availability_pct: 99.95, is_up: true, current_streak: 50 }];
    const { container } = render(<Card windows={windows} downCount={0} appName="App" />);
    expect(container.textContent).toContain("Availability");
    expect(container.textContent).toContain("99.95%");
  });
  it("shows down count", () => {
    const { container } = render(<Card windows={[]} downCount={2} appName="App" />);
    expect(container.textContent).toContain("2 down");
  });
});
