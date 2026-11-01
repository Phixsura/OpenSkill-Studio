import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamInviteManager } from "@/components/team-invite-manager";

describe("TeamInviteManager", () => {
  const invites = [
    { invite_id: "inv_1", email: "bob@example.com", role: "developer", status: "pending" },
  ];
  it("renders", () => {
    const { container } = render(
      <TeamInviteManager invites={invites} onInvite={vi.fn()} onRevoke={vi.fn()} />
    );
    expect(container.textContent).toContain("Team Invites");
    expect(container.textContent).toContain("bob@example.com");
    expect(container.textContent).toContain("pending");
  });
  it("revoke", () => {
    const fn = vi.fn();
    const { container } = render(
      <TeamInviteManager invites={invites} onInvite={vi.fn()} onRevoke={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Revoke")!);
    expect(fn).toHaveBeenCalledWith("inv_1");
  });
});
