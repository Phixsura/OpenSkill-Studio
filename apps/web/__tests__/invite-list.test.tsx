import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InviteList } from "@/components/invite-list";

describe("InviteList", () => {
  const invites = [
    { email: "alice@example.com", role: "editor", inviter: "Bob", status: "pending", expiresAt: "2026-01-05" },
    { email: "charlie@example.com", role: "viewer", inviter: "Bob", status: "accepted", expiresAt: "2026-01-04" },
  ];
  it("renders invites", () => {
    const { container } = render(<InviteList invites={invites} onRevoke={vi.fn()} onResend={vi.fn()} />);
    expect(container.textContent).toContain("alice@example.com");
    expect(container.textContent).toContain("charlie@example.com");
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("accepted");
  });
  it("revoke click", () => {
    const fn = vi.fn();
    const { container } = render(<InviteList invites={invites} onRevoke={fn} onResend={vi.fn()} />);
    const revoke = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Revoke")!;
    fireEvent.click(revoke);
    expect(fn).toHaveBeenCalledWith("alice@example.com");
  });
});
