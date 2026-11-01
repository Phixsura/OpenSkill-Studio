import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PermissionMatrix } from "@/components/permission-matrix";

describe("PermissionMatrix", () => {
  const matrix = { viewer: { read: true, write: false }, editor: { read: true, write: true } };
  const roles = ["viewer", "editor"];
  const actions = ["read", "write"];
  it("renders grid", () => {
    const { container } = render(
      <PermissionMatrix matrix={matrix} roles={roles} actions={actions} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("viewer");
    expect(container.textContent).toContain("read");
    expect(container.querySelectorAll("button").length).toBe(4);
  });
  it("toggle calls handler", () => {
    const fn = vi.fn();
    const { container } = render(
      <PermissionMatrix matrix={matrix} roles={roles} actions={actions} onToggle={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[2]); // viewer+write
    expect(fn).toHaveBeenCalledWith("viewer", "write");
  });
});
