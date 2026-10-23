import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScopeSelector } from "@/components/scope-selector";

describe("ScopeSelector", () => {
  const scopes = [
    { id: "read:apps", description: "Read app data", category: "Apps", dangerous: false },
    { id: "delete:apps", description: "Delete apps", category: "Apps", dangerous: true },
  ];
  it("renders scopes", () => {
    const { container } = render(
      <ScopeSelector scopes={scopes} selected={new Set(["read:apps"])} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("read:apps");
    expect(container.textContent).toContain("delete:apps");
    expect(container.textContent).toContain("Dangerous");
    expect(container.querySelectorAll("input[type='checkbox']").length).toBe(2);
  });
  it("toggle", () => {
    const fn = vi.fn();
    const { container } = render(
      <ScopeSelector scopes={scopes} selected={new Set()} onToggle={fn} />
    );
    fireEvent.click(container.querySelectorAll("input")[0]);
    expect(fn).toHaveBeenCalledWith("read:apps");
  });
});
