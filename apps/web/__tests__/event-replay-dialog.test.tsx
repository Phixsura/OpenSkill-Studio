import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventReplayDialog } from "@/components/event-replay-dialog";

describe("EventReplayDialog", () => {
  it("renders info", () => {
    const { container } = render(
      <EventReplayDialog eventCount={5} targetUrl="https://x.com/hook" onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("5 events");
    expect(container.textContent).toContain("https://x.com/hook");
    expect(container.textContent).toContain("handle duplicates");
  });
  it("shows replaying", () => {
    const { container } = render(
      <EventReplayDialog eventCount={1} targetUrl="x" onConfirm={vi.fn()} onCancel={vi.fn()} isReplaying />
    );
    expect(container.textContent).toContain("Replaying...");
  });
  it("calls onConfirm", () => {
    const fn = vi.fn();
    const { container } = render(
      <EventReplayDialog eventCount={1} targetUrl="x" onConfirm={fn} onCancel={vi.fn()} />
    );
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Replay")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalled();
  });
});
