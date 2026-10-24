import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PermissionMatrixGrid } from "@/components/permission-matrix-grid";

describe("PermissionMatrixGrid", () => {
  it("renders grid", () => {
    const { container } = render(
      <PermissionMatrixGrid actions={["read", "write"]} coverage={50} onToggle={vi.fn()}
        matrix={[
          { resource: "users", actions: { read: true, write: false } },
          { resource: "billing", actions: { read: true, write: true } },
        ]} />
    );
    expect(container.textContent).toContain("Permission Matrix");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("billing");
  });
});
