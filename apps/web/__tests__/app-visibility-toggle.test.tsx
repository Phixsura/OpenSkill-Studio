import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppVisibilityToggle } from "@/components/app-visibility-toggle";

describe("AppVisibilityToggle", () => {
  it("renders 3 options", () => {
    const { container } = render(<AppVisibilityToggle visibility="private" onChange={vi.fn()} />);
    expect(container.querySelectorAll("button").length).toBe(3);
  });

  it("highlights selected", () => {
    const { container } = render(<AppVisibilityToggle visibility="public" onChange={vi.fn()} />);
    const publicBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Public"));
    expect(publicBtn?.className).toContain("blue");
  });

  it("calls onChange", () => {
    const onChange = vi.fn();
    const { container } = render(<AppVisibilityToggle visibility="private" onChange={onChange} />);
    const unlisted = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Unlisted"));
    fireEvent.click(unlisted!);
    expect(onChange).toHaveBeenCalledWith("unlisted");
  });

  it("shows descriptions", () => {
    const { container } = render(<AppVisibilityToggle visibility="private" onChange={vi.fn()} />);
    expect(container.textContent).toContain("marketplace");
    expect(container.textContent).toContain("Only you");
  });
});
