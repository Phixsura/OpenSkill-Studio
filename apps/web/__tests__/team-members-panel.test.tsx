import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamMembersPanel } from "@/components/team-members-panel";

const members = [
  { userId: "u1", displayName: "Alice", role: "owner", joinedAt: Date.now() },
  { userId: "u2", displayName: "Bob", role: "developer", joinedAt: Date.now() },
];

describe("TeamMembersPanel", () => {
  it("renders members", () => {
    const { container } = render(<TeamMembersPanel members={members} />);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Bob");
    expect(container.textContent).toContain("Team Members (2)");
  });
  it("remove non-owner", () => {
    const fn = vi.fn();
    const { container } = render(<TeamMembersPanel members={members} onRemove={fn} />);
    const removeBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Remove");
    if (removeBtn) fireEvent.click(removeBtn);
    expect(fn).toHaveBeenCalledWith("u2");
  });
});
