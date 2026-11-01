import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NavSidebar } from "@/components/nav-sidebar";

describe("NavSidebar", () => {
  it("renders nav", () => {
    const onNav = vi.fn();
    const { container, getByText } = render(
      <NavSidebar onNavigate={onNav} items={[
        { id: "apps", label: "Apps", icon: "📱", path: "/apps", active: true, badge: null },
        { id: "webhooks", label: "Webhooks", icon: "🔗", path: "/webhooks", active: false, badge: 3 },
      ]} />
    );
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("3");
    fireEvent.click(getByText("Webhooks"));
    expect(onNav).toHaveBeenCalledWith("/webhooks");
  });
});
