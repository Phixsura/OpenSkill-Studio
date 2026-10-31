import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScreenshotGallery } from "@/components/screenshot-gallery";

const screenshots = [
  { screenshotId: "ss-1", url: "https://cdn.example.com/1.png", caption: "Dashboard view" },
  { screenshotId: "ss-2", url: "https://cdn.example.com/2.png", caption: "" },
];

describe("ScreenshotGallery", () => {
  it("renders gallery", () => {
    const { container } = render(<ScreenshotGallery screenshots={screenshots} />);
    expect(container.textContent).toContain("Dashboard view");
    expect(container.querySelectorAll("img").length).toBeGreaterThanOrEqual(2);
  });
  it("empty state", () => {
    const { container } = render(<ScreenshotGallery screenshots={[]} />);
    expect(container.textContent).toContain("No screenshots");
  });
});
