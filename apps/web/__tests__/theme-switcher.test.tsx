import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ThemeSwitcher } from "@/components/theme-switcher";

describe("ThemeSwitcher", () => {
  const themes = [
    { id: "light", name: "Light", preview: { bg: "#fff", text: "#000", primary: "#2563eb" } },
    { id: "dark", name: "Dark", preview: { bg: "#111", text: "#fff", primary: "#3b82f6" } },
  ];
  it("renders themes", () => {
    const { container } = render(<ThemeSwitcher themes={themes} activeTheme="light" onSwitch={vi.fn()} />);
    expect(container.textContent).toContain("Light");
    expect(container.textContent).toContain("Dark");
  });
  it("switches theme", () => {
    const fn = vi.fn();
    const { container } = render(<ThemeSwitcher themes={themes} activeTheme="light" onSwitch={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("dark");
  });
});
