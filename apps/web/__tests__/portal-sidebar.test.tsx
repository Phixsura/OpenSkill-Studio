import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PortalSidebar } from "@/components/portal-sidebar";

describe("PortalSidebar", () => {
  const items = [
    { path: "/dev", title: "Dashboard", icon: "📊" },
    { path: "/dev/apps", title: "Apps", icon: "📦" },
  ];
  it("renders items", () => {
    const { container } = render(<PortalSidebar items={items} activePath="/dev" onNavigate={vi.fn()} />);
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("Apps");
  });
  it("navigates", () => {
    const fn = vi.fn();
    const { container } = render(<PortalSidebar items={items} activePath="/dev" onNavigate={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("/dev/apps");
  });
});
