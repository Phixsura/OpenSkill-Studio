import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccessControlMemberList } from "@/components/access-control-member-list";

describe("AccessControlMemberList", () => {
  const members = [
    { user_id: "u1", display_name: "Alice", role: "owner", joined: "2026-01-01" },
    { user_id: "u2", display_name: "Bob", role: "developer", joined: "2026-06-15" },
  ];
  it("renders", () => {
    const { container } = render(
      <AccessControlMemberList members={members} currentUserRole="owner" onChangeRole={vi.fn()} onRemove={vi.fn()} />
    );
    expect(container.textContent).toContain("Team Members");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("Bob");
  });
  it("remove non-owner", () => {
    const fn = vi.fn();
    const { container } = render(
      <AccessControlMemberList members={members} currentUserRole="owner" onChangeRole={vi.fn()} onRemove={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Remove")!);
    expect(fn).toHaveBeenCalledWith("u2");
  });
});
