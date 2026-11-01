import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NavigationSidebar } from "@/components/navigation-sidebar";

describe("NavigationSidebar", () => {
  const items = [
    { path: "/", label: "Home", icon: "🏠", active: true },
    { path: "/marketplace", label: "Marketplace", icon: "🏪", active: false },
    { path: "/settings", label: "Settings", icon: "⚙️", active: false },
  ];
  it("renders", () => {
    const { container } = render(<NavigationSidebar items={items} onNavigate={vi.fn()} />);
    expect(container.textContent).toContain("🏠");
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("Settings");
  });
  it("navigate", () => {
    const fn = vi.fn();
    const { container } = render(<NavigationSidebar items={items} onNavigate={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("/marketplace");
  });
  it("collapsed hides labels", () => {
    const { container } = render(<NavigationSidebar items={items} onNavigate={vi.fn()} collapsed />);
    expect(container.textContent).toContain("🏠");
    expect(container.textContent).not.toContain("Home");
  });
});
