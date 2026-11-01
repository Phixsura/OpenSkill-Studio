import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookReplayMgr } from "@/components/webhook-replay-mgr";

describe("WebhookReplayMgr", () => {
  it("renders", () => {
    const { container } = render(
      <WebhookReplayMgr deliveryRate={67} pending={1} exhausted={1} onReplay={vi.fn()}
        replays={[
          { replayId: "r1", webhookId: "wh1", attempts: 2, maxRetries: 3, status: "retrying" },
          { replayId: "r2", webhookId: "wh2", attempts: 1, maxRetries: 3, status: "delivered" },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Replay");
    expect(container.textContent).toContain("67% delivered");
    expect(container.textContent).toContain("wh1");
    expect(container.textContent).toContain("2/3");
    expect(container.textContent).toContain("retrying");
    expect(container.textContent).toContain("delivered");
  });
});
