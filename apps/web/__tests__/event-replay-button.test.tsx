import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventReplayButton } from "@/components/event-replay-button";

describe("EventReplayButton", () => {
  it("renders replay text", () => {
    const { container } = render(<EventReplayButton eventId="e1" eventType="test" onReplay={vi.fn()} />);
    expect(container.textContent).toContain("Replay");
  });

  it("is a button", () => {
    const { container } = render(<EventReplayButton eventId="e1" eventType="test" onReplay={vi.fn()} />);
    expect(container.querySelector("button")).toBeTruthy();
  });

  it("can be disabled", () => {
    const { container } = render(<EventReplayButton eventId="e1" eventType="test" onReplay={vi.fn()} disabled />);
    expect(container.querySelector("button")?.disabled).toBe(true);
  });

  it("has title with event type", () => {
    const { container } = render(<EventReplayButton eventId="e1" eventType="submission.completed" onReplay={vi.fn()} />);
    expect(container.querySelector("button")?.title).toContain("submission.completed");
  });
});
