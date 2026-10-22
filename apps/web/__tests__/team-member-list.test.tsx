import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamMemberList } from "@/components/team-member-list";

const MEMBERS = [
  { userId: "u1", displayName: "Alice", role: "owner", email: "alice@x.com" },
  { userId: "u2", displayName: "Bob", role: "member" },
];

describe("TeamMemberList", () => {
  it("shows members", () => {
    const { container } = render(<TeamMemberList members={MEMBERS} />);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Bob");
  });
  it("shows roles", () => {
    const { container } = render(<TeamMemberList members={MEMBERS} />);
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("member");
  });
  it("no remove for owner", () => {
    const { container } = render(<TeamMemberList members={MEMBERS} onRemove={vi.fn()} />);
    const removes = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "Remove");
    assert(removes.length === 1); // only Bob can be removed
  });
  it("empty state", () => {
    const { container } = render(<TeamMemberList members={[]} />);
    expect(container.textContent).toContain("No team");
  });
});
