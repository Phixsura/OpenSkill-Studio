import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UrlShortenerForm } from "@/components/url-shortener-form";

describe("UrlShortenerForm", () => {
  it("renders form", () => {
    const { container } = render(
      <UrlShortenerForm onShorten={vi.fn()} links={[
        { shortUrl: "https://osk.io/start", slug: "start", original: "https://docs.openskill.io", clicks: 42 },
      ]} />
    );
    expect(container.textContent).toContain("URL Shortener");
    expect(container.textContent).toContain("osk.io/start");
    expect(container.textContent).toContain("42 clicks");
  });
});
