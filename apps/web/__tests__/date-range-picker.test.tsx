import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DateRangePicker } from "@/components/date-range-picker";

describe("DateRangePicker", () => {
  const presets = [
    { id: "last_7d", label: "Last 7 Days", days: 7 },
    { id: "last_30d", label: "Last 30 Days", days: 30 },
  ];
  it("renders presets", () => {
    const { container } = render(
      <DateRangePicker presets={presets} selected="last_7d" onSelect={vi.fn()} onCustom={vi.fn()} />
    );
    expect(container.textContent).toContain("Last 7 Days");
    expect(container.textContent).toContain("Last 30 Days");
    expect(container.textContent).toContain("Custom");
  });
  it("select preset", () => {
    const fn = vi.fn();
    const { container } = render(
      <DateRangePicker presets={presets} selected={null} onSelect={fn} onCustom={vi.fn()} />
    );
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Last 30 Days")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("last_30d");
  });
});
