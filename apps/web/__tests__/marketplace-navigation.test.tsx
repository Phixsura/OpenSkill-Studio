import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceNavigation } from "@/components/marketplace-navigation";

const mockItems = [
  { id: "browse", label: "Browse", icon: "🔍" },
  { id: "installed", label: "Installed", icon: "📦", badge: 3 },
  { id: "develop", label: "Develop", icon: "🛠️", children: [
    { id: "my-extensions", label: "My Extensions", icon: "📋" },
    { id: "analytics", label: "Analytics", icon: "📊" },
  ]},
  { id: "settings", label: "Settings", icon: "⚙️" },
];

describe("MarketplaceNavigation", () => {
  it("renders nav items", () => {
    const { container } = render(
      <MarketplaceNavigation items={mockItems} activeId="browse" />
    );
    expect(container.textContent).toContain("Browse");
    expect(container.textContent).toContain("Installed");
    expect(container.textContent).toContain("Develop");
    expect(container.textContent).toContain("Settings");
  });

  it("shows badge count", () => {
    const { container } = render(
      <MarketplaceNavigation items={mockItems} activeId="browse" />
    );
    expect(container.textContent).toContain("3");
  });

  it("shows children expanded by default", () => {
    const { container } = render(
      <MarketplaceNavigation items={mockItems} activeId="browse" />
    );
    expect(container.textContent).toContain("My Extensions");
    expect(container.textContent).toContain("Analytics");
  });

  it("calls onNavigate for leaf items", () => {
    const onNav = vi.fn();
    const { getByText } = render(
      <MarketplaceNavigation items={mockItems} activeId="browse" onNavigate={onNav} />
    );
    fireEvent.click(getByText("Settings"));
    expect(onNav).toHaveBeenCalledWith("settings");
  });
});
