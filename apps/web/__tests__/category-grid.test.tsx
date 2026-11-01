import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategoryGrid } from "@/components/category-grid";

describe("CategoryGrid", () => {
  it("renders categories", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <CategoryGrid onSelect={onSelect} categories={[
        { id: "analytics", label: "Analytics", icon: "📊", count: 25 },
        { id: "security", label: "Security", icon: "🔐", count: 12 },
      ]} />
    );
    expect(container.textContent).toContain("Analytics");
    expect(container.textContent).toContain("25 apps");
    expect(container.textContent).toContain("Security");
    fireEvent.click(getByText("Analytics"));
    expect(onSelect).toHaveBeenCalledWith("analytics");
  });
});
