import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScreenshotUploadGrid } from "@/components/screenshot-upload-grid";

describe("ScreenshotUploadGrid", () => {
  it("renders grid", () => {
    const onRemove = vi.fn();
    const { container, getAllByText } = render(
      <ScreenshotUploadGrid maxCount={8} onUpload={vi.fn()} onRemove={onRemove}
        screenshots={[
          { url: "https://cdn/1.png", filename: "screen1", dimensions: "1920x1080" },
        ]} />
    );
    expect(container.textContent).toContain("Screenshots");
    expect(container.textContent).toContain("1/8");
    expect(container.textContent).toContain("1920x1080");
    fireEvent.click(getAllByText("×")[0]);
    expect(onRemove).toHaveBeenCalledWith(0);
  });
});
