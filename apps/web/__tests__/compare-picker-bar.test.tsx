import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ComparePickerBar } from "@/components/compare-picker-bar";

describe("ComparePickerBar", () => {
  it("renders picker", () => {
    const onCompare = vi.fn();
    const { container, getByText } = render(
      <ComparePickerBar canCompare={true} canAdd={true} maxCompare={4}
        onRemove={vi.fn()} onCompare={onCompare}
        selected={[
          { id: "a", name: "App A", icon: "📱" },
          { id: "b", name: "App B", icon: "🔧" },
        ]} />
    );
    expect(container.textContent).toContain("Compare (2/4)");
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("App B");
    fireEvent.click(getByText("Compare"));
    expect(onCompare).toHaveBeenCalled();
  });
});
