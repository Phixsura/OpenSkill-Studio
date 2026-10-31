import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlaygroundSession } from "@/components/playground-session";

describe("PlaygroundSession", () => {
  it("renders editor", () => {
    const { container } = render(
      <PlaygroundSession sessionId="play_abc123def456" language="python"
        onRun={vi.fn(() => ({ output: "hello", executionMs: 10, memoryMb: 5 }))} />
    );
    expect(container.textContent).toContain("Playground");
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("Run");
    expect(container.querySelector("textarea")).toBeTruthy();
  });
});
