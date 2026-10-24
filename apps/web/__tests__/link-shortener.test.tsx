import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LinkShortener } from "@/components/link-shortener";

describe("LinkShortener", () => {
  const links = [
    { slug: "abc", original: "https://example.com", clicks: 150 },
  ];
  it("renders links", () => {
    const { container } = render(<LinkShortener links={links} totalClicks={150} onShorten={vi.fn()} />);
    expect(container.textContent).toContain("osk.li/abc");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("Shorten");
  });
  it("calls onShorten", () => {
    const fn = vi.fn();
    const { container } = render(<LinkShortener links={[]} totalClicks={0} onShorten={fn} />);
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "https://test.com" } });
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("https://test.com");
  });
});
