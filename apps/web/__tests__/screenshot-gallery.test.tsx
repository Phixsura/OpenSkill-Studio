import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScreenshotGallery } from "@/components/screenshot-gallery";

describe("ScreenshotGallery", () => {
  it("shows images", () => {
    const { container } = render(<ScreenshotGallery screenshots={[{ url: "img.png", alt: "Test" }]} />);
    expect(container.querySelector("img")).toBeTruthy();
  });
  it("null when empty", () => {
    const { container } = render(<ScreenshotGallery screenshots={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
