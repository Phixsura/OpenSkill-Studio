import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IconGallery } from "@/components/icon-gallery";

describe("IconGallery", () => {
  const icons = [
    { name: "home", svg: "<svg></svg>" },
    { name: "search", svg: "<svg></svg>" },
  ];
  it("renders icons", () => {
    const { container } = render(<IconGallery icons={icons} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Icons (2)");
    expect(container.textContent).toContain("home");
    expect(container.textContent).toContain("search");
  });
  it("select icon", () => {
    const fn = vi.fn();
    const { container } = render(<IconGallery icons={icons} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("home");
  });
});
