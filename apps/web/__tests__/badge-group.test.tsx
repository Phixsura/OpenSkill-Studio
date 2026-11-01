import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BadgeGroup } from "@/components/badge-group";

describe("BadgeGroup", () => {
  const badges = [
    { label: "v2.0", variant: "default", icon: null, removable: false, classes: "bg-gray-100" },
    { label: "Featured", variant: "success", icon: "⭐", removable: true, classes: "bg-green-100" },
  ];
  it("renders", () => {
    const { container } = render(<BadgeGroup badges={badges} />);
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("⭐");
    expect(container.textContent).toContain("Featured");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(<BadgeGroup badges={badges} onRemove={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "×")!);
    expect(fn).toHaveBeenCalledWith("Featured");
  });
});
