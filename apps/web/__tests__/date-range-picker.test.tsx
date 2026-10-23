import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DateRangePicker } from "@/components/date-range-picker";

describe("DateRangePicker", () => {
  const presets = [{ id: "7d", label: "7 days" }, { id: "30d", label: "30 days" }];
  it("renders", () => {
    const { container } = render(
      <DateRangePicker presets={presets} activePreset="7d"
        onPresetChange={vi.fn()} startDate="2026-10-16" endDate="2026-10-23" />
    );
    expect(container.textContent).toContain("7 days");
    expect(container.textContent).toContain("30 days");
  });
  it("preset change", () => {
    const fn = vi.fn();
    const { container } = render(
      <DateRangePicker presets={presets} activePreset="7d"
        onPresetChange={fn} startDate="2026-10-16" endDate="2026-10-23" />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "30 days")!);
    expect(fn).toHaveBeenCalledWith("30d");
  });
});
