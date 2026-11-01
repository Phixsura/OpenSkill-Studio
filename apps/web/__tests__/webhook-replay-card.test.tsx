import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookReplayCard from "../src/components/webhook-replay-card";

const deliveries = [
  { delivery_id: "d1", event_type: "push", destination: "https://a.com", original_status: 500, replay_count: 2, resolved: true },
  { delivery_id: "d2", event_type: "issue", destination: "https://b.com", original_status: 502, replay_count: 0, resolved: false },
];

describe("WebhookReplayCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<WebhookReplayCard deliveries={deliveries} pendingCount={1} resolvedCount={1} appName="App" />);
    expect(container.textContent).toContain("Webhook Replay");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("1 resolved");
  });

  it("shows event types and status", () => {
    const { container } = render(<WebhookReplayCard deliveries={deliveries} pendingCount={1} resolvedCount={1} appName="App" />);
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("2 retries");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookReplayCard deliveries={[]} pendingCount={0} resolvedCount={0} appName="App" />);
    expect(container.textContent).toContain("No failed deliveries");
  });
});
