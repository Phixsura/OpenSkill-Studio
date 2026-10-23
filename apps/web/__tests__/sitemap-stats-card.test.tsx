import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SitemapStatsCard } from "@/components/sitemap-stats-card";

describe("SitemapStatsCard", () => {
  it("renders", () => {
    const { container } = render(
      <SitemapStatsCard totalUrls={250} staticCount={20} dynamicCount={230}
        lastGenerated="2026-10-23" onRegenerate={vi.fn()} />
    );
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("20");
    expect(container.textContent).toContain("230");
    expect(container.textContent).toContain("2026-10-23");
  });
  it("regenerate", () => {
    const fn = vi.fn();
    const { container } = render(
      <SitemapStatsCard totalUrls={0} staticCount={0} dynamicCount={0}
        lastGenerated="" onRegenerate={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Regenerate"))!);
    expect(fn).toHaveBeenCalled();
  });
});
