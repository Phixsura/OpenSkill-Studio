import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PermissionPolicyEditor } from "@/components/permission-policy-editor";

describe("PermissionPolicyEditor", () => {
  it("renders policies", () => {
    const onRemove = vi.fn();
    const { container, getAllByText } = render(
      <PermissionPolicyEditor onAdd={vi.fn()} onRemove={onRemove} policies={[
        { name: "admin_all", effect: "allow", resource: "*", actions: ["*"] },
        { name: "deny_delete", effect: "deny", resource: "apps/*", actions: ["delete"] },
      ]} />
    );
    expect(container.textContent).toContain("Permission Policies");
    expect(container.textContent).toContain("ALLOW");
    expect(container.textContent).toContain("DENY");
    expect(container.textContent).toContain("admin_all");
    fireEvent.click(getAllByText("Remove")[0]);
    expect(onRemove).toHaveBeenCalledWith("admin_all");
  });
});
