import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AccessCtrlPanel } from "@/components/access-ctrl-panel";

describe("AccessCtrlPanel", () => {
  it("renders", () => {
    const { container } = render(
      <AccessCtrlPanel totalUsers={50} totalPermissions={12}
        roles={[
          { role: "admin", permissions: ["read", "write", "delete", "manage"], userCount: 5 },
          { role: "viewer", permissions: ["read"], userCount: 45 },
        ]} />
    );
    expect(container.textContent).toContain("Access Control");
    expect(container.textContent).toContain("2 roles");
    expect(container.textContent).toContain("50 users");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
    expect(container.textContent).toContain("viewer");
    expect(container.textContent).toContain("5 users");
    expect(container.textContent).toContain("45 users");
  });
});
