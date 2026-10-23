import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DragDropUploader } from "@/components/drag-drop-uploader";

describe("DragDropUploader", () => {
  it("renders drop zone", () => {
    const { container } = render(<DragDropUploader accept=".png,.jpg" maxSizeMb={50} onUpload={vi.fn()} />);
    expect(container.textContent).toContain("Drag & drop");
    expect(container.textContent).toContain("Browse");
    expect(container.textContent).toContain("50MB");
  });
});
