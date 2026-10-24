import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSidebar } from "@/components/app-sidebar";

describe("AppSidebar", () => {
  const items = [
    { id: "overview", label: "Overview", icon: "📊", href: "/apps/a1/overview", active: true, badge: null },
    { id: "reviews", label: "Reviews", icon: "⭐", href: "/apps/a1/reviews", active: false, badge: 5 },
  ];
  it("renders sidebar", () => {
    const { container } = render(<AppSidebar appName="SuperApp" items={items} onNavigate={vi.fn()} />);
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Reviews");
    expect(container.textContent).toContain("5");
  });
  it("navigates", () => {
    const fn = vi.fn();
    const { container } = render(<AppSidebar appName="X" items={items} onNavigate={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("/apps/a1/reviews");
  });
});
