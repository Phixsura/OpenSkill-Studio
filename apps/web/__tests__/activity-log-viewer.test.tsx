import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ActivityLogViewer } from "@/components/activity-log-viewer";

describe("ActivityLogViewer", () => {
  it("renders events", () => {
    const events = [{ category: "app", event_type: "app.created", actor_id: "u1", timestamp: "2026-01-01T10:00:00Z" }];
    const { container } = render(<ActivityLogViewer events={events} onFilter={vi.fn()} activeFilter={null} />);
    expect(container.textContent).toContain("app.created");
    expect(container.textContent).toContain("u1");
  });
  it("filter button", () => {
    const fn = vi.fn();
    const { container } = render(<ActivityLogViewer events={[]} onFilter={fn} activeFilter={null} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("webhook"))!);
    expect(fn).toHaveBeenCalledWith("webhook");
  });
  it("empty state", () => {
    const { container } = render(<ActivityLogViewer events={[]} onFilter={vi.fn()} activeFilter={null} />);
    expect(container.textContent).toContain("No events");
  });
});
