import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScreenshotGallery } from "@/components/screenshot-gallery";

describe("ScreenshotGallery", () => {
  const screenshots = [
    { url: "https://cdn.example.com/1.png", altText: "Dashboard", order: 1 },
    { url: "https://cdn.example.com/2.png", altText: "Settings", order: 2 },
  ];
  it("renders gallery", () => {
    const { container } = render(<ScreenshotGallery screenshots={screenshots} meetsMinimum={true} />);
    expect(container.querySelectorAll("img").length).toBeGreaterThanOrEqual(2);
    expect(container.querySelectorAll("button").length).toBe(2);
  });
  it("empty state", () => {
    const { container } = render(<ScreenshotGallery screenshots={[]} meetsMinimum={false} />);
    expect(container.textContent).toContain("No screenshots");
  });
});
