import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DebuggerPanel } from "@/components/debugger-panel";

const pausedSession = {
  state: "paused" as const,
  breakpoints: [
    { id: "bp1", file: "app.js", line: 42, type: "line", enabled: true, hitCount: 3 },
    { id: "bp2", file: "util.js", line: 10, type: "conditional", enabled: false, hitCount: 0, condition: "x > 5" },
  ],
  callStack: [
    { functionName: "handleRequest", file: "app.js", line: 42, locals: { req: "{...}", x: 42 } },
    { functionName: "main", file: "index.js", line: 5, locals: {} },
  ],
  watchExpressions: { counter: "state.count" },
};

describe("DebuggerPanel", () => {
  it("renders debug state and stack", () => {
    const { container } = render(<DebuggerPanel session={pausedSession} />);
    expect(container.textContent).toContain("Paused");
    expect(container.textContent).toContain("handleRequest");
    expect(container.textContent).toContain("app.js:42");
  });

  it("shows breakpoints", () => {
    const { getByText, container } = render(<DebuggerPanel session={pausedSession} />);
    fireEvent.click(getByText("Breakpoints (2)"));
    expect(container.textContent).toContain("app.js:42");
    expect(container.textContent).toContain("if x > 5");
    expect(container.textContent).toContain("×3");
  });

  it("calls onResume", () => {
    const onResume = vi.fn();
    const { getByText } = render(<DebuggerPanel session={pausedSession} onResume={onResume} />);
    fireEvent.click(getByText("▶ Resume"));
    expect(onResume).toHaveBeenCalled();
  });

  it("calls onStep", () => {
    const onStep = vi.fn();
    const { getByText } = render(<DebuggerPanel session={pausedSession} onStep={onStep} />);
    fireEvent.click(getByText("⤵ Step"));
    expect(onStep).toHaveBeenCalledWith("over");
  });
});
