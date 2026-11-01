import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-event-replay-policy-card";

describe("WebhookEventReplayPolicyCard", () => {
  it("shows policies", () => {
    const policies = [{ consumer_id: "c1", max_replays: 3, window_hours: 24, auto_replay: true, delay_s: 60 }];
    const { container } = render(<Card policies={policies} appName="App" />);
    expect(container.textContent).toContain("Replay Policies");
    expect(container.textContent).toContain("3×");
    expect(container.textContent).toContain("24h");
    expect(container.textContent).toContain("auto");
  });
  it("shows empty", () => {
    const { container } = render(<Card policies={[]} appName="App" />);
    expect(container.textContent).toContain("No replay policies");
  });
});
