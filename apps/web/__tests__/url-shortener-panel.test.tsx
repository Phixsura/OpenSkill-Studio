import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UrlShortenerPanel } from "@/components/url-shortener-panel";

describe("UrlShortenerPanel", () => {
  const links = [
    { short_url: "https://osk.link/abc", original_url: "https://example.com/long", slug: "abc", clicks: 42 },
  ];
  it("renders", () => {
    const { container } = render(
      <UrlShortenerPanel links={links} totalClicks={42} onCreate={vi.fn()} onCopy={vi.fn()} />
    );
    expect(container.textContent).toContain("Short Links");
    expect(container.textContent).toContain("42 total clicks");
    expect(container.textContent).toContain("osk.link/abc");
    expect(container.textContent).toContain("42 clicks");
  });
});
