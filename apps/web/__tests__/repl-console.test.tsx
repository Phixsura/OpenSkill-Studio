import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReplConsole } from "@/components/repl-console";

const mockHistory = [
  { inputCode: "let x = 42", output: "x = 42", error: "", executionTimeMs: 0.5 },
  { inputCode: "x + 1", output: "43", error: "", executionTimeMs: 0.3 },
  { inputCode: "import os", output: "", error: "Blocked: import os is not allowed", executionTimeMs: 0.1 },
];

describe("ReplConsole", () => {
  it("renders history entries", () => {
    const { container } = render(<ReplConsole history={mockHistory} runtime="node20" />);
    expect(container.textContent).toContain("let x = 42");
    expect(container.textContent).toContain("43");
    expect(container.textContent).toContain("Blocked");
  });

  it("shows runtime badge", () => {
    const { container } = render(<ReplConsole history={[]} runtime="python3.12" />);
    expect(container.textContent).toContain("python3.12");
    expect(container.textContent).toContain("Ready");
  });

  it("calls onExecute on Run click", () => {
    const onExecute = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <ReplConsole history={[]} runtime="node20" onExecute={onExecute} />
    );
    fireEvent.change(getByPlaceholderText("Enter expression..."), { target: { value: "1+1" } });
    fireEvent.click(getByText("Run"));
    expect(onExecute).toHaveBeenCalledWith("1+1");
  });

  it("calls onClear", () => {
    const onClear = vi.fn();
    const { getByText } = render(<ReplConsole history={mockHistory} runtime="node20" onClear={onClear} />);
    fireEvent.click(getByText("Clear"));
    expect(onClear).toHaveBeenCalled();
  });
});
