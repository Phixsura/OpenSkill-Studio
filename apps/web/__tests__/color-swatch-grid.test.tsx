import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ColorSwatchGrid } from "@/components/color-swatch-grid";

describe("ColorSwatchGrid", () => {
  it("renders palette", () => {
    const { container } = render(
      <ColorSwatchGrid baseColor="#3B82F6" shades={[
        { shade: 100, hex: "#dbeafe" }, { shade: 500, hex: "#3b82f6" }, { shade: 900, hex: "#1e3a5f" },
      ]} />
    );
    expect(container.textContent).toContain("Color Palette");
    expect(container.textContent).toContain("#3B82F6");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("900");
  });
});
