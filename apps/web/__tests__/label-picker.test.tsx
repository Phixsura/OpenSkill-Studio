import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LabelPicker } from "@/components/label-picker";

describe("LabelPicker", () => {
  const labels = [
    { name: "bug", color: "#EF4444", count: 10 },
    { name: "feature", color: "#3B82F6", count: 25 },
  ];
  it("renders labels", () => {
    const { container } = render(<LabelPicker labels={labels} selected={new Set(["bug"])} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("bug");
    expect(container.textContent).toContain("feature");
    expect(container.textContent).toContain("10");
  });
  it("toggle click", () => {
    const fn = vi.fn();
    const { container } = render(<LabelPicker labels={labels} selected={new Set()} onToggle={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("bug");
  });
});
