import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperRoleCard from "../src/components/api-developer-role-card";

const roles = [{ role_id: "admin", name: "Admin", permission_count: 5, member_count: 2 }];

describe("APIDeveloperRoleCard", () => {
  it("shows roles", () => {
    const { container } = render(<APIDeveloperRoleCard roles={roles} appName="App" />);
    expect(container.textContent).toContain("Developer Roles");
    expect(container.textContent).toContain("Admin");
    expect(container.textContent).toContain("5 perms");
    expect(container.textContent).toContain("2 members");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperRoleCard roles={[]} appName="App" />);
    expect(container.textContent).toContain("No roles defined");
  });
});
