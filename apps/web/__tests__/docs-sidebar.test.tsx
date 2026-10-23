import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DocsSidebar } from "@/components/docs-sidebar";

describe("DocsSidebar", () => {
  const sections = [{
    title: "Getting Started", icon: "🚀", expanded: true,
    pages: [{ title: "Installation", path: "/docs/install", active: true }],
  }];
  it("renders sidebar", () => {
    const { container } = render(<DocsSidebar sections={sections} onNavigate={vi.fn()} />);
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Installation");
  });
  it("navigate click", () => {
    const fn = vi.fn();
    const { container } = render(<DocsSidebar sections={sections} onNavigate={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("/docs/install");
  });
});
