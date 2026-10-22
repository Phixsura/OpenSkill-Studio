import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SeoHead } from "@/components/seo-head";

describe("SeoHead", () => {
  it("renders title", () => {
    const { container } = render(<SeoHead title="Test Page" description="A test" />);
    expect(container.querySelector("title")?.textContent).toBe("Test Page");
  });
  it("renders meta description", () => {
    const { container } = render(<SeoHead title="X" description="My description" />);
    expect(container.querySelector("meta[name='description']")?.getAttribute("content")).toBe("My description");
  });
  it("renders og tags", () => {
    const { container } = render(<SeoHead title="X" description="Y" ogImage="https://img.com/icon.png" />);
    expect(container.querySelector("meta[property='og:image']")?.getAttribute("content")).toContain("icon.png");
  });
});
