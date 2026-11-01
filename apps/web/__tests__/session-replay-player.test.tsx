import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SessionReplayPlayer } from "@/components/session-replay-player";

describe("SessionReplayPlayer", () => {
  it("renders replay", () => {
    const { container } = render(
      <SessionReplayPlayer sessionId="s1" userId="u1" startPage="/dashboard"
        durationDisplay="3.0s" totalEvents={3} errorCount={1} events={[
          { type: "click", target: "button.save", timestampMs: 1000 },
          { type: "error", target: "api/users", timestampMs: 3000 },
        ]} />
    );
    expect(container.textContent).toContain("Session Replay");
    expect(container.textContent).toContain("3.0s");
    expect(container.textContent).toContain("3 events");
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("click");
    expect(container.textContent).toContain("error");
  });
});
