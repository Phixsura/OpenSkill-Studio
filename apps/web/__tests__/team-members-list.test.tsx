import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamMembersList } from "@/components/team-members-list";

describe("TeamMembersList", () => {
  it("renders members", () => {
    const members = [
      { id: "1", email: "owner@test.com", role: "owner", status: "active" },
      { id: "2", email: "dev@test.com", role: "developer", status: "pending" },
    ];
    const { container } = render(<TeamMembersList members={members} onRemove={vi.fn()} onChangeRole={vi.fn()} />);
    expect(container.textContent).toContain("owner@test.com");
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("Team Members (2)");
  });
  it("no remove for owner", () => {
    const members = [{ id: "1", email: "x", role: "owner", status: "active" }];
    const { container } = render(<TeamMembersList members={members} onRemove={vi.fn()} onChangeRole={vi.fn()} />);
    expect(container.querySelector("button")).toBeNull();
  });
});
