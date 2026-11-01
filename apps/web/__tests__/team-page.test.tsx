import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamPage } from "@/components/team-page";

describe("TeamPage", () => {
  const members = [{ id: "u1", name: "Alice", email: "a@b.com", role: "owner", roleIcon: "👑", active: true }];
  const invites = [{ email: "bob@b.com", role: "editor", sentAt: "2026-01-01" }];
  it("renders team page", () => {
    const { container } = render(
      <TeamPage orgName="Acme" members={members} pendingInvites={invites}
        onRemove={vi.fn()} onInvite={vi.fn()} onRevokeInvite={vi.fn()} />
    );
    expect(container.textContent).toContain("Acme Team");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("Pending Invites (1)");
    expect(container.textContent).toContain("bob@b.com");
  });
});
