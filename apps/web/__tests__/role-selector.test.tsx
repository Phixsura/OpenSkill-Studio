import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RoleSelector } from "@/components/role-selector";

describe("RoleSelector", () => {
  it("renders roles", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <RoleSelector currentRole="member" onSelect={onSelect}
        canAssign={(r) => r !== "owner"}
        roles={[
          { role: "viewer", level: 0, permissionCount: 1 },
          { role: "member", level: 1, permissionCount: 2 },
          { role: "admin", level: 3, permissionCount: 5 },
        ]} />
    );
    expect(container.textContent).toContain("viewer");
    expect(container.textContent).toContain("member");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("5 permissions");
    fireEvent.click(getByText("admin"));
    expect(onSelect).toHaveBeenCalledWith("admin");
  });
});
