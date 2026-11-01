import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamPageLayout } from "@/components/team-page-layout";

describe("TeamPageLayout", () => {
  it("renders", () => {
    const stats = { total: 3, pending_invites: 1, plan_limit: 5, seats_remaining: 2 };
    const { container } = render(
      <TeamPageLayout stats={stats} canInvite={true} onInvite={vi.fn()}>
        <p>Members list</p>
      </TeamPageLayout>
    );
    expect(container.textContent).toContain("3 members");
    expect(container.textContent).toContain("2 seats remaining");
    expect(container.textContent).toContain("1 pending invite");
    expect(container.textContent).toContain("Members list");
  });
  it("full team", () => {
    const stats = { total: 5, pending_invites: 0, plan_limit: 5, seats_remaining: 0 };
    const { container } = render(
      <TeamPageLayout stats={stats} canInvite={false} onInvite={vi.fn()}>
        <p>C</p>
      </TeamPageLayout>
    );
    expect(container.textContent).toContain("Team Full");
  });
  it("invite click", () => {
    const fn = vi.fn();
    const stats = { total: 1, pending_invites: 0, plan_limit: 5, seats_remaining: 4 };
    const { container } = render(
      <TeamPageLayout stats={stats} canInvite={true} onInvite={fn}><p>C</p></TeamPageLayout>
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Invite"))!);
    expect(fn).toHaveBeenCalled();
  });
});
