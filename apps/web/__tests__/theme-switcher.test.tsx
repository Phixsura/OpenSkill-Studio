import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ThemeSwitcher } from "@/components/theme-switcher";

describe("ThemeSwitcher", () => {
  it("renders themes", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <ThemeSwitcher current="light" onSelect={onSelect} presets={[
        { name: "light", previewBg: "#FFFFFF", previewPrimary: "#3B82F6" },
        { name: "dark", previewBg: "#111827", previewPrimary: "#60A5FA" },
        { name: "midnight", previewBg: "#0F172A", previewPrimary: "#818CF8" },
      ]} />
    );
    expect(container.textContent).toContain("Theme");
    expect(container.textContent).toContain("light");
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("midnight");
    fireEvent.click(getByText("dark"));
    expect(onSelect).toHaveBeenCalledWith("dark");
  });
});
