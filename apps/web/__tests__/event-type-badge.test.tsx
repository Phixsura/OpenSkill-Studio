import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventTypeBadge } from "@/components/event-type-badge";

const EVENT_TYPES = [
  "submission.completed", "submission.graded",
  "cohort.member_added", "project.published",
  "pack.published", "workflow.run_completed",
  "app.installed", "evaluation.completed",
];

describe("EventTypeBadge", () => {
  it.each(EVENT_TYPES)("renders %s", (eventType) => {
    const { container } = render(<EventTypeBadge eventType={eventType} />);
    expect(container.querySelector("span")).toBeTruthy();
    expect(container.textContent).toContain(eventType);
  });

  it("renders unknown event type", () => {
    const { container } = render(<EventTypeBadge eventType="custom.event" />);
    expect(container.textContent).toContain("custom.event");
  });
});
