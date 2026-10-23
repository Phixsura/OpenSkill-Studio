import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ColorModeToggle } from "@/components/color-mode-toggle";

describe("ColorModeToggle", () => {
  it("renders", () => {
    const { container } = render(<ColorModeToggle currentMode="light" onModeChange={vi.fn()} />);
    expect(container.textContent).toContain("☀️");
    expect(container.textContent).toContain("🌙");
    expect(container.textContent).toContain("💻");
    expect(container.querySelectorAll("button").length).toBe(3);
  });
  it("changes mode", () => {
    const fn = vi.fn();
    const { container } = render(<ColorModeToggle currentMode="light" onModeChange={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]); // dark
    expect(fn).toHaveBeenCalledWith("dark");
  });
});
