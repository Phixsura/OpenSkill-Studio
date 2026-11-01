import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamRoster } from "@/components/team-roster";

describe("TeamRoster", () => {
  const members = [
    { id: "1", name: "Alice", email: "a@b.com", role: "owner", active: true, joinedAt: "2026-01-01" },
    { id: "2", name: "Bob", email: "b@b.com", role: "editor", active: true, joinedAt: "2026-02-01" },
  ];
  it("renders members", () => {
    const { container } = render(<TeamRoster members={members} onChangeRole={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("Bob");
    expect(container.textContent).toContain("Team (2)");
  });
  it("remove non-owner", () => {
    const fn = vi.fn();
    const { container } = render(<TeamRoster members={members} onChangeRole={vi.fn()} onRemove={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("2");
  });
});
