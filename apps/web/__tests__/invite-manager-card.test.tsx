import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import InviteManagerCard from "../src/components/invite-manager-card";

const invites = [
  {
    invite_id: "i1",
    email: "alice@example.com",
    role: "admin",
    status: "pending" as const,
    created_at: new Date(Date.now() - 3_600_000).toISOString(),
  },
  {
    invite_id: "i2",
    email: "bob@example.com",
    role: "member",
    status: "accepted" as const,
    created_at: new Date(Date.now() - 86_400_000).toISOString(),
  },
  {
    invite_id: "i3",
    email: "carol@example.com",
    role: "viewer",
    status: "expired" as const,
    created_at: new Date(Date.now() - 259_200_000).toISOString(),
  },
];

describe("InviteManagerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<InviteManagerCard invites={invites} appName="My App" />);
    expect(container.textContent).toContain("Invitations");
    expect(container.textContent).toContain("My App");
  });

  it("shows pending count", () => {
    const { container } = render(<InviteManagerCard invites={invites} appName="App" />);
    expect(container.textContent).toContain("1 pending");
  });

  it("renders emails", () => {
    const { container } = render(<InviteManagerCard invites={invites} appName="App" />);
    expect(container.textContent).toContain("alice@example.com");
    expect(container.textContent).toContain("bob@example.com");
  });

  it("shows roles", () => {
    const { container } = render(<InviteManagerCard invites={invites} appName="App" />);
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("member");
  });

  it("shows status labels", () => {
    const { container } = render(<InviteManagerCard invites={invites} appName="App" />);
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("accepted");
    expect(container.textContent).toContain("expired");
  });

  it("shows empty state", () => {
    const { container } = render(<InviteManagerCard invites={[]} appName="App" />);
    expect(container.textContent).toContain("No invitations");
  });
});
