import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickActionsMenu } from "@/components/quick-actions-menu";

describe("QuickActionsMenu", () => {
  const actions = [
    { id: "update", label: "Update", icon: "🔄", primary: true },
    { id: "settings", label: "Settings", icon: "⚙️" },
    { id: "delete", label: "Delete", icon: "🗑️", danger: true },
  ];
  it("shows primary action", () => {
    const { container } = render(<QuickActionsMenu actions={actions} onAction={vi.fn()} />);
    expect(container.textContent).toContain("Update");
  });
  it("opens menu", () => {
    const { container } = render(<QuickActionsMenu actions={actions} onAction={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "⋮")!);
    expect(container.textContent).toContain("Settings");
    expect(container.textContent).toContain("Delete");
  });
  it("calls onAction", () => {
    const fn = vi.fn();
    const { container } = render(<QuickActionsMenu actions={actions} onAction={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]); // primary
    expect(fn).toHaveBeenCalledWith("update");
  });
});
