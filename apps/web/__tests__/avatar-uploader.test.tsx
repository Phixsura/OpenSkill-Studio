import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AvatarUploader } from "@/components/avatar-uploader";

describe("AvatarUploader", () => {
  it("renders with initials", () => {
    const { container } = render(
      <AvatarUploader currentUrl="" userName="Alice Chen" initials="AC"
        onUpload={vi.fn()} uploading={false} />
    );
    expect(container.textContent).toContain("AC");
    expect(container.textContent).toContain("Alice Chen");
    expect(container.textContent).toContain("Click camera to change");
  });
});
