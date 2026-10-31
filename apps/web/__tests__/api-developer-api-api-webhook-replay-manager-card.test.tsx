import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookReplayManagerCard from "../src/components/api-developer-api-api-webhook-replay-manager-card";

const replays = [
  { replay_id: "r1", event_type: "push", destination: "https://a.com", status: "success" },
  { replay_id: "r2", event_type: "issue", destination: "https://a.com", status: "pending" },
];

describe("APIDeveloperAPIApiWebhookReplayManagerCard", () => {
  it("shows replays", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookReplayManagerCard replays={replays} stats={{ pending: 1, success: 1, failure: 0, replaying: 0 }} appName="App" />);
    expect(container.textContent).toContain("Webhook Replays");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("success: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookReplayManagerCard replays={[]} stats={{}} appName="App" />);
    expect(container.textContent).toContain("No replays");
  });
});
