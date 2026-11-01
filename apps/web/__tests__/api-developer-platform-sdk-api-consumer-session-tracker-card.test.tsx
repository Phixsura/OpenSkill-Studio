import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiConsumerSessionTrackerCard from "../src/components/api-developer-platform-sdk-api-consumer-session-tracker-card";

const sessions = [
  { session_id: "s1", consumer_id: "acme", request_count: 150, endpoints_count: 8, active: true },
  { session_id: "s2", consumer_id: "beta", request_count: 30, endpoints_count: 2, active: false },
];

describe("Card", () => {
  it("shows sessions", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerSessionTrackerCard sessions={sessions} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Active Sessions");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("150 reqs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerSessionTrackerCard sessions={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No sessions");
  });
});
