import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogEntryForm } from "@/components/changelog-entry-form";

describe("ChangelogEntryForm", () => {
  it("renders form", () => {
    const { container } = render(<ChangelogEntryForm onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Add Changelog Entry");
    expect(container.textContent).toContain("Added");
    expect(container.textContent).toContain("Fixed");
    expect(container.textContent).toContain("Add Entry");
    expect(container.querySelector("input")).toBeTruthy();
  });
});
