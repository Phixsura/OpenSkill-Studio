import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-session-manager-card";

describe("ConsumerApiSessionManagerCard", () => {
  it("shows sessions", () => {
    const sessions = [{ id: "abc123", ip: "1.2.3.4", userAgent: "curl/7.0", lastActive: "5m ago", created: "1h ago" }];
    const { container } = render(<Card sessions={sessions} consumerId="c1" maxSessions={10} appName="App" />);
    expect(container.textContent).toContain("Active Sessions");
    expect(container.textContent).toContain("abc123");
    expect(container.textContent).toContain("1.2.3.4");
    expect(container.textContent).toContain("1/10 sessions");
  });
  it("shows empty", () => {
    const { container } = render(<Card sessions={[]} consumerId="c1" maxSessions={10} appName="App" />);
    expect(container.textContent).toContain("No active sessions");
  });
});
