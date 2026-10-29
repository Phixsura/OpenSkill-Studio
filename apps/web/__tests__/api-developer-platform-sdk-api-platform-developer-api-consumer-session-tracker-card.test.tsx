import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-session-tracker-card";

describe("SessionTrackerCard", () => {
  it("shows sessions", () => {
    const sessions = [{ session_id: "s1", consumer_id: "c1", request_count: 42, idle_minutes: 3 }];
    const { container } = render(<Card sessions={sessions} uniqueConsumers={1} idleCount={0} appName="App" />);
    expect(container.textContent).toContain("Active Sessions");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("42 reqs");
  });
  it("shows idle count", () => {
    const { container } = render(<Card sessions={[]} uniqueConsumers={0} idleCount={3} appName="App" />);
    expect(container.textContent).toContain("3 idle");
  });
});
