import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SitemapStatsPanel } from "@/components/sitemap-stats-panel";

const stats = { totalUrls: 500, extensions: 300, categories: 20, developers: 150, docs: 30 };

describe("SitemapStatsPanel", () => {
  it("renders stats", () => {
    const { container } = render(<SitemapStatsPanel stats={stats} />);
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("300");
    expect(container.textContent).toContain("150");
  });
  it("calls onRegenerate", () => {
    const fn = vi.fn();
    const { getByText } = render(<SitemapStatsPanel stats={stats} onRegenerate={fn} />);
    fireEvent.click(getByText("Regenerate"));
    expect(fn).toHaveBeenCalled();
  });
});
