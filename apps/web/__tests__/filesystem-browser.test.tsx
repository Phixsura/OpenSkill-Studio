import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FilesystemBrowser } from "@/components/filesystem-browser";

describe("FilesystemBrowser", () => {
  it("renders files", () => {
    const files = [{ path: "app.js", size: 2048 }, { path: "style.css", size: 512 }];
    const { container } = render(
      <FilesystemBrowser files={files} usedBytes={2560} quotaBytes={50000} onDelete={vi.fn()} />
    );
    expect(container.textContent).toContain("app.js");
    expect(container.textContent).toContain("2.0KB");
  });
  it("empty state", () => {
    const { container } = render(<FilesystemBrowser files={[]} usedBytes={0} quotaBytes={1000} onDelete={vi.fn()} />);
    expect(container.textContent).toContain("No files");
  });
});
