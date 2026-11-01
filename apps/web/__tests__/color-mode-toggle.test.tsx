import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ColorModeToggle } from "@/components/color-mode-toggle";

describe("ColorModeToggle", () => {
  it("renders toggle", () => {
    const onSelect = vi.fn();
    const { container, getByTitle } = render(
      <ColorModeToggle current="dark" onSelect={onSelect} />
    );
    expect(container.textContent).toContain("☀️");
    expect(container.textContent).toContain("🌙");
    expect(container.textContent).toContain("💻");
    fireEvent.click(getByTitle("Light"));
    expect(onSelect).toHaveBeenCalledWith("light");
  });
});
