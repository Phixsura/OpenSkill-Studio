import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookReplayPanel } from "@/components/webhook-replay-panel";

describe("WebhookReplayPanel", () => {
  it("renders and retries", () => {
    const onReplay = vi.fn();
    const { container, getByText } = render(
      <WebhookReplayPanel queueSize={1} onReplay={onReplay} onReplayAll={vi.fn()}
        entries={[{ id: "wr_abc", url: "https://example.com/hook", originalStatus: 500,
                    replayCount: 1, error: "Timeout" }]} />
    );
    expect(container.textContent).toContain("Webhook Replay Queue");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("HTTP 500");
    expect(container.textContent).toContain("1 retries");
    fireEvent.click(getByText("Retry"));
    expect(onReplay).toHaveBeenCalledWith("wr_abc");
  });
});
