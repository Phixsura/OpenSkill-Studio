import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamRolesTable } from "@/components/team-roles-table";

describe("TeamRolesTable", () => {
  it("renders members", () => {
    const { container } = render(
      <TeamRolesTable roles={["owner", "admin", "developer", "viewer"]}
        onChangeRole={vi.fn()} onRemove={vi.fn()}
        members={[
          { userId: "alice", role: "owner", addedBy: "system" },
          { userId: "bob", role: "developer", addedBy: "alice" },
        ]} />
    );
    expect(container.textContent).toContain("Team Members");
    expect(container.textContent).toContain("2 members");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("developer");
  });
});
