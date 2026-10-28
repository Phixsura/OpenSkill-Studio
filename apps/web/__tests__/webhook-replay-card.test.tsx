import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookReplayCard from "../src/components/webhook-replay-card";

const replays = [
  {
    replay_id: "rp-1",
    original_event_id: "evt-100",
    status: "queued" as const,
    attempt: 0,
    max_attempts: 3,
    error: "",
  },
  {
    replay_id: "rp-2",
    original_event_id: "evt-101",
    status: "succeeded" as const,
    attempt: 2,
    max_attempts: 3,
    error: "",
  },
  {
    replay_id: "rp-3",
    original_event_id: "evt-102",
    status: "failed" as const,
    attempt: 3,
    max_attempts: 3,
    error: "timeout",
  },
];

describe("WebhookReplayCard", () => {
  it("renders header", () => {
    const { container } = render(<WebhookReplayCard replays={replays} appName="My App" />);
    expect(container.textContent).toContain("Webhook Replay");
  });

  it("shows pending count", () => {
    const { container } = render(<WebhookReplayCard replays={replays} appName="App" />);
    expect(container.textContent).toContain("1 pending");
  });

  it("renders event ids", () => {
    const { container } = render(<WebhookReplayCard replays={replays} appName="App" />);
    expect(container.textContent).toContain("evt-100");
    expect(container.textContent).toContain("evt-102");
  });

  it("shows attempt counts", () => {
    const { container } = render(<WebhookReplayCard replays={replays} appName="App" />);
    expect(container.textContent).toContain("2/3");
  });

  it("shows error", () => {
    const { container } = render(<WebhookReplayCard replays={replays} appName="App" />);
    expect(container.textContent).toContain("timeout");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookReplayCard replays={[]} appName="App" />);
    expect(container.textContent).toContain("No replay requests");
  });
});
