import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-replay-card";

describe("WebhookReplayCard", () => {
  it("shows stats and recent", () => {
    const stats = { total: 10, pending: 2, success: 6, failed: 2 };
    const recent = [{ replay_id: "r1", consumer_id: "c1", status: "success", response_status: 200 }];
    const { container } = render(<Card stats={stats} recent={recent} appName="App" />);
    expect(container.textContent).toContain("Webhook Replay");
    expect(container.textContent).toContain("2 pending");
    expect(container.textContent).toContain("10");
  });
  it("shows empty", () => {
    const stats = { total: 0, pending: 0, success: 0, failed: 0 };
    const { container } = render(<Card stats={stats} recent={[]} appName="App" />);
    expect(container.textContent).toContain("Webhook Replay");
  });
});
