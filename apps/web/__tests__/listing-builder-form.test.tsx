import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ListingBuilderForm } from "@/components/listing-builder-form";

describe("ListingBuilderForm", () => {
  it("renders form", () => {
    const { container } = render(<ListingBuilderForm completeness={50} />);
    expect(container.textContent).toContain("Listing Builder");
    expect(container.textContent).toContain("50%");
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.querySelector("textarea")).toBeTruthy();
  });
  it("save draft", () => {
    const fn = vi.fn();
    const { container } = render(<ListingBuilderForm completeness={0} onSave={fn} />);
    const saveBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Save"));
    if (saveBtn) fireEvent.click(saveBtn);
    expect(fn).toHaveBeenCalled();
  });
});
