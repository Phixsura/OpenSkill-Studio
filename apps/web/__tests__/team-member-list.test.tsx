import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamMemberList } from "@/components/team-member-list";

describe("TeamMemberList", () => {
  it("renders team", () => {
    const onRemove = vi.fn();
    const { container, getByText } = render(
      <TeamMemberList canManage={true} onChangeRole={vi.fn()} onRemove={onRemove}
        members={[
          { name: "Alice", email: "a@t.com", role: "owner", avatarInitials: "A" },
          { name: "Bob", email: "b@t.com", role: "developer", avatarInitials: "B" },
        ]} />
    );
    expect(container.textContent).toContain("Team (2)");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("Bob");
    expect(container.textContent).toContain("developer");
    fireEvent.click(getByText("Remove"));
    expect(onRemove).toHaveBeenCalledWith("b@t.com");
  });
});
