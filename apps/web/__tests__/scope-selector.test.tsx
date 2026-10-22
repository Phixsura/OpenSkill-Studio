import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScopeSelector } from "@/components/scope-selector";

describe("ScopeSelector", () => {
  it("renders scope groups", () => {
    const { container } = render(<ScopeSelector selected={[]} onChange={vi.fn()} />);
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
    expect(container.textContent).toContain("special");
  });

  it("shows scope buttons", () => {
    const { container } = render(<ScopeSelector selected={[]} onChange={vi.fn()} />);
    const buttons = container.querySelectorAll("button");
    expect(buttons.length).toBeGreaterThan(10);
  });

  it("highlights selected scopes", () => {
    const { container } = render(<ScopeSelector selected={["read:cohorts"]} onChange={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "read:cohorts");
    expect(btn?.className).toContain("blue");
  });

  it("calls onChange on toggle", () => {
    const onChange = vi.fn();
    const { container } = render(<ScopeSelector selected={[]} onChange={onChange} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "read:cohorts");
    if (btn) fireEvent.click(btn);
    expect(onChange).toHaveBeenCalled();
  });

  it("shows count", () => {
    const { container } = render(<ScopeSelector selected={["read:cohorts", "write:projects"]} onChange={vi.fn()} />);
    expect(container.textContent).toContain("2 scopes");
  });

  it("disables unavailable scopes", () => {
    const { container } = render(<ScopeSelector selected={[]} onChange={vi.fn()} maxScopes={["read:cohorts"]} />);
    const writeBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent?.startsWith("write:"));
    for (const btn of writeBtns) {
      expect(btn.hasAttribute("disabled")).toBe(true);
    }
  });
});
