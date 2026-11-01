import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccessPolicyPanel } from "@/components/access-policy-panel";

const mockRoles = [
  { name: "admin", ruleCount: 3, inherits: [] },
  { name: "editor", ruleCount: 2, inherits: ["viewer"] },
  { name: "viewer", ruleCount: 1, inherits: [] },
];
const mockAssignments = [
  { userId: "alice", role: "admin" },
  { userId: "bob", role: "editor" },
];
const mockRules = [
  { resource: "files:*", actions: ["read", "write"], decision: "allow" as const },
  { resource: "files:secrets", actions: ["read"], decision: "deny" as const },
];

describe("AccessPolicyPanel", () => {
  it("renders roles", () => {
    const { container } = render(
      <AccessPolicyPanel roles={mockRoles} assignments={mockAssignments} selectedRoleRules={null} />
    );
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("editor");
    expect(container.textContent).toContain("← viewer");
  });

  it("shows assignments tab", () => {
    const { getByText, container } = render(
      <AccessPolicyPanel roles={mockRoles} assignments={mockAssignments} selectedRoleRules={null} />
    );
    fireEvent.click(getByText("Assignments (2)"));
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("admin");
  });

  it("expands to show rules", () => {
    const onSelect = vi.fn();
    const { getByText, container } = render(
      <AccessPolicyPanel roles={mockRoles} assignments={[]} selectedRoleRules={mockRules} onSelectRole={onSelect} />
    );
    fireEvent.click(getByText("admin"));
    expect(onSelect).toHaveBeenCalledWith("admin");
    expect(container.textContent).toContain("files:*");
    expect(container.textContent).toContain("deny");
  });
});
