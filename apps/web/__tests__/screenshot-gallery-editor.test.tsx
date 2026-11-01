import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScreenshotGalleryEditor } from "@/components/screenshot-gallery-editor";

describe("ScreenshotGalleryEditor", () => {
  const screenshots = [
    { id: "s1", url: "a.png", position: 0 },
    { id: "s2", url: "b.png", position: 1 },
  ];
  it("renders", () => {
    const { container } = render(
      <ScreenshotGalleryEditor screenshots={screenshots} onReorder={vi.fn()} onDelete={vi.fn()} onUpload={vi.fn()} />
    );
    expect(container.textContent).toContain("Screenshots");
    expect(container.textContent).toContain("a.png");
    expect(container.textContent).toContain("b.png");
  });
  it("delete", () => {
    const fn = vi.fn();
    const { container } = render(
      <ScreenshotGalleryEditor screenshots={screenshots} onReorder={vi.fn()} onDelete={fn} onUpload={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Delete")!);
    expect(fn).toHaveBeenCalledWith("s1");
  });
});
