import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlaygroundPresetSelector } from "@/components/playground-preset-selector";

describe("PlaygroundPresetSelector", () => {
  it("renders presets", () => {
    const { container } = render(<PlaygroundPresetSelector selected="default" onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Minimal");
    expect(container.textContent).toContain("Default");
    expect(container.textContent).toContain("Full Power");
  });
  it("selects preset", () => {
    const fn = vi.fn();
    const { container } = render(<PlaygroundPresetSelector selected="default" onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[2]); // Full Power
    expect(fn).toHaveBeenCalledWith("full");
  });
});
