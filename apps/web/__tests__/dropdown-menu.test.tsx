import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DropdownMenu } from "@/components/dropdown-menu";

describe("DropdownMenu", () => {
  const items = [
    { id: "edit", label: "Edit", icon: "✏️", danger: false, separator_before: false, disabled: false },
    { id: "delete", label: "Delete", icon: "🗑️", danger: true, separator_before: true, disabled: false },
  ];
  it("opens on trigger click", () => {
    const { container } = render(
      <DropdownMenu trigger={<button>Menu</button>} items={items} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Menu");
    expect(container.textContent).not.toContain("Edit");
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("Edit");
    expect(container.textContent).toContain("Delete");
    expect(container.textContent).toContain("✏️");
  });
});
