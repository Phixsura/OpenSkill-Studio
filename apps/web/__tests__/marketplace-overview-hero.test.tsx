import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceOverviewHero } from "@/components/marketplace-overview-hero";

const mockStats = { extensions: 245, developers: 120, installs: 89000, categories: 12 };

describe("MarketplaceOverviewHero", () => {
  it("renders title and stats", () => {
    const { container } = render(<MarketplaceOverviewHero stats={mockStats} />);
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("245");
    expect(container.textContent).toContain("120");
    expect(container.textContent).toContain("89,000");
    expect(container.textContent).toContain("12");
  });

  it("calls onBrowse", () => {
    const onBrowse = vi.fn();
    const { getByText } = render(<MarketplaceOverviewHero stats={mockStats} onBrowse={onBrowse} />);
    fireEvent.click(getByText("🔍 Browse Extensions"));
    expect(onBrowse).toHaveBeenCalled();
  });

  it("calls onPublish", () => {
    const onPublish = vi.fn();
    const { getByText } = render(<MarketplaceOverviewHero stats={mockStats} onPublish={onPublish} />);
    fireEvent.click(getByText("📦 Publish Yours"));
    expect(onPublish).toHaveBeenCalled();
  });
});
