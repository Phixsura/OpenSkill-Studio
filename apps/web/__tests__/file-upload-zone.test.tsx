import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FileUploadZone } from "@/components/file-upload-zone";

describe("FileUploadZone", () => {
  it("renders", () => {
    const { container } = render(
      <FileUploadZone category="image" maxSizeMb={5} allowedTypes={[".png", ".jpg"]}
        onUpload={vi.fn()} />
    );
    expect(container.textContent).toContain("image Upload");
    expect(container.textContent).toContain("Max 5MB");
    expect(container.textContent).toContain(".png");
    expect(container.textContent).toContain("Drag & drop");
  });
});
