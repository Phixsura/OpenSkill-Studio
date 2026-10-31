import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickActionBar } from "@/components/quick-action-bar";

const actions = [
  { actionId: "a1", name: "Deploy", icon: "🚀", dangerous: false, requiresConfirm: false, executionCount: 5 },
  { actionId: "a2", name: "Reset DB", icon: "💣", dangerous: true, requiresConfirm: true, executionCount: 0 },
];

describe("QuickActionBar", () => {
  it("renders actions", () => {
    const { container } = render(<QuickActionBar actions={actions} />);
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("Reset DB");
    expect(container.textContent).toContain("×5");
  });
  it("calls onExecute", () => {
    const fn = vi.fn();
    const { getByText } = render(<QuickActionBar actions={actions} onExecute={fn} />);
    fireEvent.click(getByText("Deploy"));
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
