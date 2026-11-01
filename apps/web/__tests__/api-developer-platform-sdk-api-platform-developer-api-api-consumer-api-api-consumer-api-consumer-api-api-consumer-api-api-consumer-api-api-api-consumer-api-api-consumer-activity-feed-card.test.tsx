import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-api-consumer-activity-feed-card";

describe("ConsumerActivityFeedCard", () => {
  it("shows events", () => {
    const events = [{ id: "e1", actor: "admin", action: "created", resourceType: "api_key", resourceId: "k1", description: "", timestamp: "5m ago" }];
    const { container } = render(<Card events={events} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Activity Feed");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("api_key/k1");
  });
  it("shows empty", () => {
    const { container } = render(<Card events={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No recent activity");
  });
});
