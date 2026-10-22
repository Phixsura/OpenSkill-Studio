import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppSidebarNav } from "@/components/app-sidebar-nav";

const ITEMS = [
  { label: "Overview", href: "/app/overview", icon: "📊", active: true },
  { label: "Versions", href: "/app/versions", icon: "📦" },
  { label: "Webhooks", href: "/app/webhooks", icon: "🔔", badge: 3 },
];

describe("AppSidebarNav", () => {
  it("renders items", () => {
    const { container } = render(<AppSidebarNav items={ITEMS} />);
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Versions");
  });

  it("highlights active", () => {
    const { container } = render(<AppSidebarNav items={ITEMS} />);
    const active = container.querySelector("a[class*='blue']");
    expect(active?.textContent).toContain("Overview");
  });

  it("shows badge", () => {
    const { container } = render(<AppSidebarNav items={ITEMS} />);
    expect(container.textContent).toContain("3");
  });

  it("has links", () => {
    const { container } = render(<AppSidebarNav items={ITEMS} />);
    expect(container.querySelectorAll("a").length).toBe(3);
  });
});
