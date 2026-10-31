import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PendingInvitesList } from "@/components/pending-invites-list";

describe("PendingInvitesList", () => {
  it("renders invites", () => {
    const onResend = vi.fn();
    const onRevoke = vi.fn();
    const { container, getByText } = render(
      <PendingInvitesList onResend={onResend} onRevoke={onRevoke}
        invites={[{ email: "bob@test.com", role: "editor", status: "pending" }]} />
    );
    expect(container.textContent).toContain("Pending Invites");
    expect(container.textContent).toContain("bob@test.com");
    expect(container.textContent).toContain("editor");
    fireEvent.click(getByText("Resend"));
    expect(onResend).toHaveBeenCalledWith("bob@test.com");
    fireEvent.click(getByText("Revoke"));
    expect(onRevoke).toHaveBeenCalledWith("bob@test.com");
  });
});
