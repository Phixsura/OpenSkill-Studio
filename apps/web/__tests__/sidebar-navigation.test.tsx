import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SidebarNavigation } from "@/components/sidebar-navigation";

describe("SidebarNavigation", () => {
  it("renders sidebar", () => {
    const onNav = vi.fn();
    const { container, getByText } = render(
      <SidebarNavigation collapsed={false} onNavigate={onNav} onToggle={vi.fn()} items={[
        { id: "dashboard", label: "Dashboard", icon: "🏠", path: "/dashboard", active: true, badge: null },
        { id: "webhooks", label: "Webhooks", icon: "🔗", path: "/webhooks", active: false, badge: 3 },
      ]} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("3");
    fireEvent.click(getByText("Webhooks"));
    expect(onNav).toHaveBeenCalledWith("/webhooks");
  });
});
