import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PillSelector } from "@/components/pill-selector";

describe("PillSelector", () => {
  const pills = [
    { id: "a", label: "Alpha", icon: null, selected: true, disabled: false },
    { id: "b", label: "Beta", icon: "🔵", selected: false, disabled: false },
  ];
  it("renders", () => {
    const { container } = render(
      <PillSelector pills={pills} selectedCount={1} maxSelect={3} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("Alpha");
    expect(container.textContent).toContain("✕");
    expect(container.textContent).toContain("Beta");
    expect(container.textContent).toContain("1/3");
  });
  it("toggle", () => {
    const fn = vi.fn();
    const { container } = render(
      <PillSelector pills={pills} selectedCount={1} maxSelect={null} onToggle={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("b");
  });
});
