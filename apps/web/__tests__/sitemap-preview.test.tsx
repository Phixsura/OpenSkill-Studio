import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SitemapPreview } from "@/components/sitemap-preview";

describe("SitemapPreview", () => {
  const entries = [
    { url: "https://example.com/", lastmod: "2026-01-01", changefreq: "daily", priority: 1.0 },
    { url: "https://example.com/apps", lastmod: "2026-01-01", changefreq: "weekly", priority: 0.8 },
  ];
  it("renders sitemap entries", () => {
    const { container } = render(<SitemapPreview entries={entries} sizeBytes={512} />);
    expect(container.textContent).toContain("Sitemap");
    expect(container.textContent).toContain("2 URLs");
    expect(container.textContent).toContain("example.com");
    expect(container.textContent).toContain("daily");
  });
});
