import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GradientPicker } from "@/components/gradient-picker";

describe("GradientPicker", () => {
  const presets = [
    { id: "sunset", css: "linear-gradient(to right, #F97316, #EC4899)", from: "#F97316", to: "#EC4899" },
    { id: "ocean", css: "linear-gradient(to right, #3B82F6, #06B6D4)", from: "#3B82F6", to: "#06B6D4" },
  ];
  it("renders presets", () => {
    const { container } = render(<GradientPicker presets={presets} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("sunset");
    expect(container.textContent).toContain("ocean");
    expect(container.querySelectorAll("button").length).toBe(2);
  });
  it("selects preset", () => {
    const fn = vi.fn();
    const { container } = render(<GradientPicker presets={presets} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith(presets[0].css);
  });
});
