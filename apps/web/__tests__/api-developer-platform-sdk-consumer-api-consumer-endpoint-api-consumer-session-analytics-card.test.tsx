import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-api-consumer-session-analytics-card";

describe("ConsumerSessionAnalyticsCard", () => {
  it("shows analytics", () => {
    const { container } = render(<Card consumerId="c1" totalSessions={150} avgDurationSec={300} avgRequests={25} avgEndpoints={4} longestSec={1800} mostVisited="/api/users" activeSessions={3} appName="App" />);
    expect(container.textContent).toContain("Session Analytics");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("5m");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("3 active");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" totalSessions={0} avgDurationSec={0} avgRequests={0} avgEndpoints={0} longestSec={0} mostVisited="" activeSessions={0} appName="App" />);
    expect(container.textContent).toContain("0");
  });
});
