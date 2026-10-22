import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ManifestPatchEditor } from "@/components/manifest-patch-editor";

describe("ManifestPatchEditor", () => {
  it("renders form", () => {
    const { container } = render(<ManifestPatchEditor onApply={vi.fn()} />);
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.querySelectorAll("input").length).toBeGreaterThanOrEqual(1);
  });

  it("has add button", () => {
    const { container } = render(<ManifestPatchEditor onApply={vi.fn()} />);
    expect(container.textContent).toContain("Add");
  });

  it("has op options", () => {
    const { container } = render(<ManifestPatchEditor onApply={vi.fn()} />);
    const select = container.querySelector("select")!;
    expect(select.querySelectorAll("option").length).toBe(3);
  });
});
