import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FileUploadZone } from "@/components/file-upload-zone";

describe("FileUploadZone", () => {
  it("renders zone", () => {
    const { container } = render(
      <FileUploadZone category="image" maxMb={10} allowedExtensions={[".png", ".jpg"]}
        onUpload={vi.fn()} uploading={false}
        lastResult={{ valid: true, filename: "logo.png" }} />
    );
    expect(container.textContent).toContain("Upload image");
    expect(container.textContent).toContain(".png, .jpg");
    expect(container.textContent).toContain("Max 10MB");
    expect(container.textContent).toContain("logo.png uploaded");
  });
});
