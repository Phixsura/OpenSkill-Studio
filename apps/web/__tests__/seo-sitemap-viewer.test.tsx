import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SeoSitemapViewer } from "@/components/seo-sitemap-viewer";

describe("SeoSitemapViewer", () => {
  const urls = [
    { loc: "https://marketplace.dev/", priority: 0.8, changefreq: "weekly" },
    { loc: "https://marketplace.dev/apps/auth", priority: 0.6, changefreq: "daily" },
  ];
  it("renders", () => {
    const { container } = render(
      <SeoSitemapViewer urls={urls} totalUrls={11} staticPages={6} dynamicPages={5} onGenerate={vi.fn()} />
    );
    expect(container.textContent).toContain("Sitemap");
    expect(container.textContent).toContain("11");
    expect(container.textContent).toContain("marketplace.dev/");
    expect(container.textContent).toContain("Regenerate");
  });
});
