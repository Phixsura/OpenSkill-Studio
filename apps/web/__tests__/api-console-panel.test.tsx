import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiConsolePanel } from "@/components/api-console-panel";

const envs = [
  { envId: "e1", name: "Dev", isActive: true, varCount: 3 },
  { envId: "e2", name: "Prod", isActive: false, varCount: 5 },
];

describe("ApiConsolePanel", () => {
  it("renders envs", () => {
    const { container } = render(<ApiConsolePanel envs={envs} />);
    expect(container.textContent).toContain("Dev (3)");
    expect(container.textContent).toContain("Prod (5)");
  });
  it("calls onExecute", () => {
    const fn = vi.fn();
    const { getByText } = render(<ApiConsolePanel envs={envs} onExecute={fn} />);
    fireEvent.click(getByText("Send"));
    expect(fn).toHaveBeenCalled();
  });
  it("switches env", () => {
    const fn = vi.fn();
    const { getByText } = render(<ApiConsolePanel envs={envs} onSetEnv={fn} />);
    fireEvent.click(getByText("Prod (5)"));
    expect(fn).toHaveBeenCalledWith("e2");
  });
});
