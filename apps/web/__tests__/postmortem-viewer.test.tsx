import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PostmortemViewer } from "@/components/postmortem-viewer";

describe("PostmortemViewer", () => {
  it("renders postmortem", () => {
    const { container } = render(
      <PostmortemViewer incidentId="INC-1" title="Database Outage" severity="critical"
        rootCause="Connection pool exhaustion" progressPct={50}
        actionItems={[
          { task: "Add connection limits", done: true },
          { task: "Add alerting", done: false },
        ]} />
    );
    expect(container.textContent).toContain("Database Outage");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("INC-1");
    expect(container.textContent).toContain("Connection pool exhaustion");
    expect(container.textContent).toContain("50% complete");
    expect(container.textContent).toContain("Add connection limits");
  });
});
