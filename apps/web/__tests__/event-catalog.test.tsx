import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventCatalog } from "@/components/event-catalog";

const CATALOG = { submission: { description: "Submission events", events: { "submission.completed": "Work submitted" } } };

describe("EventCatalog", () => {
  it("shows categories", () => {
    const { container } = render(<EventCatalog catalog={CATALOG} />);
    expect(container.textContent).toContain("submission");
  });
  it("shows events", () => {
    const { container } = render(<EventCatalog catalog={CATALOG} />);
    expect(container.textContent).toContain("submission.completed");
    expect(container.textContent).toContain("Work submitted");
  });
  it("has search", () => {
    const { container } = render(<EventCatalog catalog={CATALOG} />);
    expect(container.querySelector("input")).toBeTruthy();
  });
});
