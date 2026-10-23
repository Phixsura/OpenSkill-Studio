import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceNavBar } from "@/components/marketplace-nav-bar";

describe("MarketplaceNavBar", () => {
  const items = [
    { id: "explore", label: "Explore", url: "/marketplace", icon: "🏪", active: true },
    { id: "trending", label: "Trending", url: "/marketplace/trending", icon: "🔥", active: false, badge: "5" },
  ];
  it("renders nav", () => {
    const { container } = render(<MarketplaceNavBar items={items} onNavigate={vi.fn()} />);
    expect(container.textContent).toContain("Explore");
    expect(container.textContent).toContain("Trending");
    expect(container.textContent).toContain("5");
  });
  it("navigates", () => {
    const fn = vi.fn();
    const { container } = render(<MarketplaceNavBar items={items} onNavigate={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("/marketplace/trending");
  });
});
