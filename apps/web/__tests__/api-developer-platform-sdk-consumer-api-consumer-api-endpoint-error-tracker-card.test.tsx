import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-api-endpoint-error-tracker-card";

describe("EndpointErrorTrackerCard", () => {
  it("shows errors", () => {
    const summary = { endpoint: "/api/users", totalErrors: 50, errorRate: 2.5, mostCommon: "RATE_LIMITED", byStatus: { "429": 40, "500": 10 } };
    const errors = [{ id: "e1", statusCode: 429, errorCode: "RATE_LIMITED", message: "Too many", timestamp: "12:00" }];
    const { container } = render(<Card summary={summary} recentErrors={errors} appName="App" />);
    expect(container.textContent).toContain("Error Tracker");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("2.5%");
    expect(container.textContent).toContain("RATE_LIMITED");
  });
  it("shows zero errors", () => {
    const summary = { endpoint: "/api", totalErrors: 0, errorRate: 0, mostCommon: "", byStatus: {} };
    const { container } = render(<Card summary={summary} recentErrors={[]} appName="App" />);
    expect(container.textContent).toContain("0");
  });
});
