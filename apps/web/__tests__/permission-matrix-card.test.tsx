import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PermissionMatrixCard from "../src/components/permission-matrix-card";

const adminRole = {
  role_id: "admin",
  name: "Administrator",
  inherits_from: null,
  permissions: [
    { resource: "projects", action: "*", source: "wildcard" as const },
    { resource: "users", action: "read", source: "direct" as const },
    { resource: "users", action: "write", source: "direct" as const },
  ],
};

const editorRole = {
  role_id: "editor",
  name: "Editor",
  inherits_from: "viewer",
  permissions: [
    { resource: "projects", action: "write", source: "direct" as const },
    { resource: "projects", action: "read", source: "inherited" as const },
  ],
};

const emptyRole = {
  role_id: "guest",
  name: "Guest",
  inherits_from: null,
  permissions: [],
};

describe("PermissionMatrixCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<PermissionMatrixCard roles={[adminRole]} appName="My App" />);
    expect(container.textContent).toContain("Permission Matrix");
    expect(container.textContent).toContain("My App");
  });

  it("shows role and permission counts", () => {
    const { container } = render(
      <PermissionMatrixCard roles={[adminRole, editorRole]} appName="App" />,
    );
    expect(container.textContent).toContain("2 roles");
    expect(container.textContent).toContain("5 permissions");
  });

  it("renders role name and id", () => {
    const { container } = render(<PermissionMatrixCard roles={[adminRole]} appName="App" />);
    expect(container.textContent).toContain("Administrator");
    expect(container.textContent).toContain("admin");
  });

  it("shows inheritance indicator", () => {
    const { container } = render(<PermissionMatrixCard roles={[editorRole]} appName="App" />);
    expect(container.textContent).toContain("← viewer");
  });

  it("renders permission badges with resource:action", () => {
    const { container } = render(<PermissionMatrixCard roles={[adminRole]} appName="App" />);
    expect(container.textContent).toContain("projects:*");
    expect(container.textContent).toContain("users:read");
  });

  it("shows source labels for non-direct permissions", () => {
    const { container } = render(
      <PermissionMatrixCard roles={[adminRole, editorRole]} appName="App" />,
    );
    expect(container.textContent).toContain("(Wildcard)");
    expect(container.textContent).toContain("(Inherited)");
  });

  it("shows no-permissions label for empty role", () => {
    const { container } = render(<PermissionMatrixCard roles={[emptyRole]} appName="App" />);
    expect(container.textContent).toContain("No permissions");
  });

  it("shows empty state when no roles", () => {
    const { container } = render(<PermissionMatrixCard roles={[]} appName="App" />);
    expect(container.textContent).toContain("No roles configured");
  });

  it("shows singular count for one role", () => {
    const { container } = render(<PermissionMatrixCard roles={[emptyRole]} appName="App" />);
    expect(container.textContent).toContain("1 role");
    expect(container.textContent).not.toContain("1 roles");
  });
});
