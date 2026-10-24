import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PermPolicyViewer } from "@/components/perm-policy-viewer";

describe("PermPolicyViewer", () => {
  it("renders", () => {
    const { container } = render(
      <PermPolicyViewer
        userPermissions={["read", "write"]}
        policies={[
          { name: "editor_access", effect: "allow", actions: ["read", "write"], conditions: "role=editor" },
        ]} />
    );
    expect(container.textContent).toContain("Permission Policies");
    expect(container.textContent).toContain("1 policies");
    expect(container.textContent).toContain("2 perms");
    expect(container.textContent).toContain("editor_access");
    expect(container.textContent).toContain("allow");
    expect(container.textContent).toContain("read, write");
  });
});
