import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StorageBrowser } from "@/components/storage-browser";

const objects = [{ key: "assets/logo.png", sizeBytes: 50000, contentType: "image/png", uploadedAt: Date.now(), isPublic: true }];
const usage = { objectCount: 1, totalBytes: 50000 };

describe("StorageBrowser", () => {
  it("renders files", () => {
    const { container } = render(<StorageBrowser objects={objects} usage={usage} />);
    expect(container.textContent).toContain("assets/logo.png");
    expect(container.textContent).toContain("public");
    expect(container.textContent).toContain("1 objects");
  });
  it("delete file", () => {
    const fn = vi.fn();
    const { container } = render(<StorageBrowser objects={objects} usage={usage} onDelete={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("assets/logo.png");
  });
});
