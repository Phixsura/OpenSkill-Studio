import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InviteLinkCard } from "@/components/invite-link-card";

describe("InviteLinkCard", () => {
  it("renders and revokes", () => {
    const onRevoke = vi.fn();
    const { container, getByText } = render(
      <InviteLinkCard url="https://app.openskill.io/invite/abc123" code="abc123"
        role="admin" maxUses={10} uses={3} onRevoke={onRevoke} />
    );
    expect(container.textContent).toContain("Invite Link");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("3 / 10 uses");
    fireEvent.click(getByText("Revoke"));
    expect(onRevoke).toHaveBeenCalledWith("abc123");
  });
});
