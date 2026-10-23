import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickActionBar } from "@/components/quick-action-bar";

describe("QuickActionBar", () => {
  const actions = [
    { id: "restart", label: "Restart", icon: "🔄", danger: false, confirm: false },
    { id: "delete", label: "Delete", icon: "🗑️", danger: true, confirm: true },
  ];
  it("renders", () => {
    const { container } = render(<QuickActionBar actions={actions} onExecute={vi.fn()} />);
    expect(container.textContent).toContain("🔄");
    expect(container.textContent).toContain("Restart");
    expect(container.textContent).toContain("🗑️");
    expect(container.textContent).toContain("Delete");
  });
  it("execute", () => {
    const fn = vi.fn();
    const { container } = render(<QuickActionBar actions={actions} onExecute={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("restart");
  });
});
