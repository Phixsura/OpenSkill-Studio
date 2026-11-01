import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ColorPicker } from "@/components/color-picker";

describe("ColorPicker", () => {
  const presets = [
    { name: "blue", hex: "#3B82F6" },
    { name: "green", hex: "#10B981" },
  ];
  it("renders presets and selected", () => {
    const { container } = render(<ColorPicker presets={presets} selected="#3B82F6" onChange={vi.fn()} />);
    expect(container.textContent).toContain("Brand Color");
    expect(container.textContent).toContain("#3B82F6");
    expect(container.querySelectorAll("button").length).toBeGreaterThanOrEqual(2);
  });
  it("calls onChange on preset click", () => {
    const fn = vi.fn();
    const { container } = render(<ColorPicker presets={presets} selected="" onChange={fn} />);
    const buttons = container.querySelectorAll("button");
    fireEvent.click(buttons[0]);
    expect(fn).toHaveBeenCalledWith("#3B82F6");
  });
});
