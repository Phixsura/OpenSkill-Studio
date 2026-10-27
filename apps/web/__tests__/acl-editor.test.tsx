import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AclEditor } from "@/components/acl-editor";

const rules = [
  { resource: "/api/data", principal: "user-1", permissions: ["read", "write"] },
  { resource: "/settings", principal: "role:admin", permissions: ["admin"] },
];

describe("AclEditor", () => {
  it("renders rules", () => {
    const { container } = render(<AclEditor rules={rules} />);
    expect(container.textContent).toContain("/api/data");
    expect(container.textContent).toContain("user-1");
    expect(container.textContent).toContain("admin");
  });
  it("revoke action", () => {
    const fn = vi.fn();
    const { container } = render(<AclEditor rules={rules} onRevoke={fn} />);
    const btns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "Revoke");
    fireEvent.click(btns[0]);
    expect(fn).toHaveBeenCalledWith("/api/data", "user-1");
  });
});
