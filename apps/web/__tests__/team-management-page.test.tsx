import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamManagementPage } from "@/components/team-management-page";

describe("TeamManagementPage", () => {
  const members = [
    { id: "u1", name: "Alice", email: "a@b.com", role: "owner", roleLabel: "Owner", roleIcon: "👑", active: true },
    { id: "u2", name: "Bob", email: "b@b.com", role: "editor", roleLabel: "Editor", roleIcon: "✏️", active: true },
  ];
  it("renders team page", () => {
    const { container } = render(
      <TeamManagementPage members={members} pendingInvites={1} seatsRemaining={8}
        canInvite={true} onInvite={vi.fn()} onRemove={vi.fn()} onChangeRole={vi.fn()} />
    );
    expect(container.textContent).toContain("Team");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Owner");
    expect(container.textContent).toContain("8 seats left");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("Invite");
  });
});
