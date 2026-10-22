import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventSchemaViewer } from "@/components/event-schema-viewer";

describe("EventSchemaViewer", () => {
  it("shows event type", () => {
    const { container } = render(<EventSchemaViewer eventType="submission.completed" required={["submission_id"]} optional={["score"]} />);
    expect(container.textContent).toContain("submission.completed");
  });

  it("shows required fields", () => {
    const { container } = render(<EventSchemaViewer eventType="x" required={["id", "name"]} optional={[]} />);
    expect(container.textContent).toContain("id");
    expect(container.textContent).toContain("Required");
  });

  it("shows optional fields", () => {
    const { container } = render(<EventSchemaViewer eventType="x" required={[]} optional={["score"]} />);
    expect(container.textContent).toContain("score");
    expect(container.textContent).toContain("Optional");
  });
});
