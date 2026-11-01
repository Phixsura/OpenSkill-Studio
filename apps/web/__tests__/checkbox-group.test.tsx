import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CheckboxGroup } from "@/components/checkbox-group";

describe("CheckboxGroup", () => {
  const items = [
    { value: "a", label: "Alpha", checked: true, disabled: false },
    { value: "b", label: "Beta", checked: false, disabled: false },
    { value: "c", label: "Gamma", checked: false, disabled: true },
  ];
  it("renders", () => {
    const { container } = render(
      <CheckboxGroup name="tags" label="Tags" items={items} selectedCount={1}
        maxSelect={2} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("Tags");
    expect(container.textContent).toContain("(1/2)");
    expect(container.textContent).toContain("Alpha");
    expect(container.textContent).toContain("Beta");
    expect(container.querySelectorAll("input[type='checkbox']").length).toBe(3);
  });
  it("toggle", () => {
    const fn = vi.fn();
    const { container } = render(
      <CheckboxGroup name="x" label="X" items={items} selectedCount={1}
        maxSelect={null} onToggle={fn} />
    );
    fireEvent.click(container.querySelectorAll("input")[1]);
    expect(fn).toHaveBeenCalledWith("b");
  });
});
