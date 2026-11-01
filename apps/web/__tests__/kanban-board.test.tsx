import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KanbanBoard } from "@/components/kanban-board";

describe("KanbanBoard", () => {
  const columns = [
    { id: "todo", title: "To Do", card_count: 1, wip_limit: null, over_limit: false,
      cards: [{ id: "1", title: "Fix bug", assignee: "Alice", priority: "high", labels: [] }] },
    { id: "done", title: "Done", card_count: 0, wip_limit: 5, over_limit: false, cards: [] },
  ];
  it("renders columns and cards", () => {
    const { container } = render(<KanbanBoard columns={columns} />);
    expect(container.textContent).toContain("To Do");
    expect(container.textContent).toContain("Done");
    expect(container.textContent).toContain("Fix bug");
    expect(container.textContent).toContain("Alice");
  });
  it("shows wip limit", () => {
    const { container } = render(<KanbanBoard columns={columns} />);
    expect(container.textContent).toContain("0/5");
  });
});
