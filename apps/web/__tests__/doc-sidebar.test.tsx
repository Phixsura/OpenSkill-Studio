import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DocSidebar } from "@/components/doc-sidebar";

describe("DocSidebar", () => {
  const items = [
    { slug: "intro", title: "Introduction", children: [] },
    { slug: "api", title: "API", children: [{ slug: "auth", title: "Auth" }] },
  ];
  it("renders items", () => {
    const { container } = render(<DocSidebar items={items} activeSlug="intro" onNavigate={vi.fn()} />);
    expect(container.textContent).toContain("Introduction");
    expect(container.textContent).toContain("Auth");
  });
  it("navigates on click", () => {
    const fn = vi.fn();
    const { container } = render(<DocSidebar items={items} activeSlug="" onNavigate={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]);
    expect(fn).toHaveBeenCalledWith("intro");
  });
});
