import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventTypeList } from "@/components/event-type-list";

const EVENTS = [
  { name: "submission.completed", category: "submission", description: "Submission done" },
  { name: "app.installed", category: "app", description: "App installed" },
];

describe("EventTypeList", () => {
  it("shows events", () => {
    const { container } = render(<EventTypeList events={EVENTS} />);
    expect(container.textContent).toContain("submission.completed");
    expect(container.textContent).toContain("app.installed");
  });

  it("filters by category", () => {
    const { container } = render(<EventTypeList events={EVENTS} selectedCategory="app" />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).not.toContain("submission.completed");
  });

  it("calls onSelect", () => {
    const onSelect = vi.fn();
    const { container } = render(<EventTypeList events={EVENTS} onSelect={onSelect} />);
    fireEvent.click(container.querySelectorAll("li")[0]);
    expect(onSelect).toHaveBeenCalledWith("submission.completed");
  });

  it("empty state", () => {
    const { container } = render(<EventTypeList events={[]} />);
    expect(container.textContent).toContain("No events");
  });
});
