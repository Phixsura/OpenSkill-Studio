import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventReplayConfig } from "@/components/event-replay-config";

describe("EventReplayConfig", () => {
  it("renders form", () => {
    const { container } = render(<EventReplayConfig onReplay={vi.fn()} />);
    expect(container.textContent).toContain("Event Replay");
    expect(container.textContent).toContain("Dry run");
    expect(container.textContent).toContain("Preview Replay");
  });
  it("submits config", () => {
    const fn = vi.fn();
    const { container } = render(<EventReplayConfig onReplay={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(expect.objectContaining({ dryRun: true }));
  });
});
