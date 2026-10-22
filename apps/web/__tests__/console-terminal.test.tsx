import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConsoleTerminal } from "@/components/console-terminal";

describe("ConsoleTerminal", () => {
  it("renders history", () => {
    const history = [{ input: "1+1", output: "2" }, { input: "err", output: "", error: "SyntaxError" }];
    const { container } = render(<ConsoleTerminal history={history} onExecute={vi.fn()} language="javascript" />);
    expect(container.textContent).toContain("1+1");
    expect(container.textContent).toContain("2");
    expect(container.textContent).toContain("SyntaxError");
  });
  it("shows language", () => {
    const { container } = render(<ConsoleTerminal history={[]} onExecute={vi.fn()} language="python" />);
    expect(container.textContent).toContain("python");
  });
});
