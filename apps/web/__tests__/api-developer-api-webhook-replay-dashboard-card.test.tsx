import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookReplayDashboardCard from "../src/components/api-developer-api-webhook-replay-dashboard-card";

const dash = { total_replayed: 100, successful_replays: 90, failed_replays: 10, pending_replay: 5, replay_success_rate: 90, avg_replay_latency_ms: 250 };

describe("APIDeveloperAPIWebhookReplayDashboardCard", () => {
  it("shows replay stats", () => {
    const { container } = render(<APIDeveloperAPIWebhookReplayDashboardCard dashboard={dash} appName="App" />);
    expect(container.textContent).toContain("Replay Dashboard");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("250ms");
  });
});
