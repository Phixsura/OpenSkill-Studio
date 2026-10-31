import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DropdownMenu } from "@/components/dropdown-menu";

describe("DropdownMenu", () => {
  it("renders menu", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <DropdownMenu onSelect={onSelect} sections={[
        { group: "actions", items: [
          { id: "edit", label: "Edit", icon: "✏️", shortcut: "⌘E", disabled: false, danger: false },
          { id: "duplicate", label: "Duplicate", icon: "📋", shortcut: "", disabled: false, danger: false },
        ]},
        { group: "danger", items: [
          { id: "delete", label: "Delete", icon: "🗑️", shortcut: "", disabled: false, danger: true },
        ]},
      ]} />
    );
    expect(container.textContent).toContain("Edit");
    expect(container.textContent).toContain("⌘E");
    expect(container.textContent).toContain("Delete");
    fireEvent.click(getByText("Edit"));
    expect(onSelect).toHaveBeenCalledWith("edit");
  });
});
