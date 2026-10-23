import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventReplayPanel } from "@/components/event-replay-panel";

describe("EventReplayPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EventReplayPanel replayId="rpl_abc" eventCount={10} speed={2}
        delivered={7} failed={1} progressPct={70} status="in_progress"
        onPause={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Event Replay");
    expect(container.textContent).toContain("rpl_abc");
    expect(container.textContent).toContain("2x speed");
    expect(container.textContent).toContain("70%");
    expect(container.textContent).toContain("✅ 7");
    expect(container.textContent).toContain("❌ 1");
    expect(container.textContent).toContain("Pause");
  });
});
