import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SessionReplayList } from "@/components/session-replay-list";

describe("SessionReplayList", () => {
  const recordings = [
    { recording_id: "rec_1", user_id: "u1", page_url: "/dashboard", duration_formatted: "1m 30s",
      has_errors: true, has_rage_clicks: false, event_count: 42 },
  ];
  it("renders", () => {
    const { container } = render(
      <SessionReplayList recordings={recordings} frustrationScore={15} onPlay={vi.fn()} />
    );
    expect(container.textContent).toContain("Session Replays");
    expect(container.textContent).toContain("/dashboard");
    expect(container.textContent).toContain("42 events");
    expect(container.textContent).toContain("❌ Error");
  });
  it("play", () => {
    const fn = vi.fn();
    const { container } = render(
      <SessionReplayList recordings={recordings} frustrationScore={15} onPlay={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("rec_1");
  });
});
