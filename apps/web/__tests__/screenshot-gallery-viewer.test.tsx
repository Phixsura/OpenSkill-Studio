import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScreenshotGalleryViewer } from "@/components/screenshot-gallery-viewer";

describe("ScreenshotGalleryViewer", () => {
  const screenshots = [
    { index: 0, url: "s1.png", alt: "Dashboard view", thumbnail_url: "t1.png" },
    { index: 1, url: "s2.png", alt: "Settings page", thumbnail_url: "t2.png" },
  ];
  it("renders gallery", () => {
    const { container } = render(<ScreenshotGalleryViewer screenshots={screenshots} />);
    expect(container.textContent).toContain("Dashboard view");
    expect(container.textContent).toContain("1 / 2");
  });
  it("switches screenshot", () => {
    const { container } = render(<ScreenshotGalleryViewer screenshots={screenshots} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(container.textContent).toContain("Settings page");
    expect(container.textContent).toContain("2 / 2");
  });
  it("empty state", () => {
    const { container } = render(<ScreenshotGalleryViewer screenshots={[]} />);
    expect(container.textContent).toContain("No screenshots");
  });
});
