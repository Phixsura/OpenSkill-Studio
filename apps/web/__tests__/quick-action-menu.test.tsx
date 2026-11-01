import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickActionMenu } from "@/components/quick-action-menu";

describe("QuickActionMenu", () => {
  const actions = [
    { id: "edit", label: "Edit", icon: "✏️", shortcut: "E", danger: false },
    { id: "delete", label: "Delete", icon: "🗑️", shortcut: null, danger: true },
  ];
  it("renders actions", () => {
    const { container } = render(<QuickActionMenu actions={actions} onAction={vi.fn()} onClose={vi.fn()} />);
    expect(container.textContent).toContain("Edit");
    expect(container.textContent).toContain("Delete");
    expect(container.textContent).toContain("E");
  });
  it("action click", () => {
    const fn = vi.fn();
    const { container } = render(<QuickActionMenu actions={actions} onAction={fn} onClose={vi.fn()} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("edit");
  });
});
