import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RbacRoleComparison } from "@/components/rbac-role-comparison";

describe("RbacRoleComparison", () => {
  it("renders comparison", () => {
    const { container } = render(
      <RbacRoleComparison roleA="admin" roleB="editor"
        shared={["apps.view", "content.view"]}
        onlyA={["users.manage", "settings.manage"]}
        onlyB={[]} />
    );
    expect(container.textContent).toContain("Role Comparison");
    expect(container.textContent).toContain("admin vs editor");
    expect(container.textContent).toContain("users.manage");
    expect(container.textContent).toContain("apps.view");
    expect(container.textContent).toContain("Shared (2)");
  });
});
