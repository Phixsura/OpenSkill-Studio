import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ColorPaletteEditor } from "@/components/color-palette-editor";

describe("ColorPaletteEditor", () => {
  const palette = [
    { shade: 100, color: "#1e3a5f" },
    { shade: 200, color: "#2d5a8e" },
    { shade: 300, color: "#3b82f6" },
  ];
  it("renders", () => {
    const { container } = render(
      <ColorPaletteEditor primary="#3b82f6" palette={palette} onPrimaryChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Brand Colors");
    expect(container.textContent).toContain("#3b82f6");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("300");
    expect(container.querySelector("input[type='color']")).toBeTruthy();
  });
});
