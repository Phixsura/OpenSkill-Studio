import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PermissionPolicyCard from "../src/components/permission-policy-card";

const roles = [
  { role_id: "admin", name: "Admin", permissions: [{ resource: "app", action: "admin" }] },
  {
    role_id: "viewer",
    name: "Viewer",
    permissions: [
      { resource: "app", action: "read" },
      { resource: "webhook", action: "read" },
    ],
  },
];

describe("PermissionPolicyCard", () => {
  it("renders header and role count", () => {
    const { container } = render(<PermissionPolicyCard roles={roles} appName="App" />);
    expect(container.textContent).toContain("Permission Policy");
    expect(container.textContent).toContain("2 roles");
  });

  it("shows role names and perm counts", () => {
    const { container } = render(<PermissionPolicyCard roles={roles} appName="App" />);
    expect(container.textContent).toContain("Admin");
    expect(container.textContent).toContain("1 perms");
    expect(container.textContent).toContain("Viewer");
    expect(container.textContent).toContain("2 perms");
  });

  it("shows permission keys", () => {
    const { container } = render(<PermissionPolicyCard roles={roles} appName="App" />);
    expect(container.textContent).toContain("app:admin");
    expect(container.textContent).toContain("webhook:read");
  });

  it("shows empty state", () => {
    const { container } = render(<PermissionPolicyCard roles={[]} appName="App" />);
    expect(container.textContent).toContain("No roles defined");
  });
});
