import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SidebarNav } from "@/components/sidebar-nav";

describe("SidebarNav", () => {
  const sections = {
    main: [
      { label: "Dashboard", path: "/dash", icon: "🏠", active: true, badge: null },
      { label: "Apps", path: "/apps", icon: "📦", active: false, badge: "3" },
    ],
  };
  it("renders nav", () => {
    const { container } = render(<SidebarNav sections={sections} onNavigate={vi.fn()} />);
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("3");
  });
  it("navigate click", () => {
    const fn = vi.fn();
    const { container } = render(<SidebarNav sections={sections} onNavigate={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("/apps");
  });
});
