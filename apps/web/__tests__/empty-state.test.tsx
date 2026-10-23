import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmptyState } from "@/components/empty-state";

describe("EmptyState", () => {
  it("renders", () => {
    const { container } = render(<EmptyState title="No apps" message="Create one!" icon="📦" />);
    expect(container.textContent).toContain("No apps");
    expect(container.textContent).toContain("Create one!");
    expect(container.textContent).toContain("📦");
  });
  it("action button", () => {
    const fn = vi.fn();
    const { container } = render(<EmptyState title="Empty" message="M" icon="X" action="Add" onAction={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
  it("no button without action", () => {
    const { container } = render(<EmptyState title="T" message="M" icon="X" />);
    expect(container.querySelector("button")).toBeNull();
  });
});
