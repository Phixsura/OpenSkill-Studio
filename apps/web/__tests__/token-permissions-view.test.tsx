import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenPermissionsView } from "@/components/token-permissions-view";

describe("TokenPermissionsView", () => {
  const groups = {
    Read: [{ id: "read:apps", label: "View apps", icon: "📦", granted: true }],
    Admin: [{ id: "admin:billing", label: "Manage billing", icon: "💳", granted: false }],
  };
  it("renders permissions", () => {
    const { container } = render(
      <TokenPermissionsView groups={groups} granted={1} total={2} hasAdmin={false} />
    );
    expect(container.textContent).toContain("Token Permissions");
    expect(container.textContent).toContain("View apps");
    expect(container.textContent).toContain("Manage billing");
    expect(container.textContent).toContain("1/2");
  });
});
