import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SitemapPreview } from "@/components/sitemap-preview";

describe("SitemapPreview", () => {
  const pages = [
    { path: "/", lastmod: "2026-10-23", priority: 1.0 },
    { path: "/apps", priority: 0.8 },
  ];
  it("renders", () => {
    const { container } = render(
      <SitemapPreview pages={pages} baseUrl="https://marketplace.dev" onGenerate={vi.fn()} />
    );
    expect(container.textContent).toContain("Sitemap");
    expect(container.textContent).toContain("2 URLs");
    expect(container.textContent).toContain("https://marketplace.dev/");
    expect(container.textContent).toContain("pri: 1");
  });
});
