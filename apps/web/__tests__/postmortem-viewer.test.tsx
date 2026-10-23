import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PostmortemViewer } from "@/components/postmortem-viewer";

describe("PostmortemViewer", () => {
  it("renders postmortem", () => {
    const { container } = render(
      <PostmortemViewer title="DB Outage" severity="sev1" mttrDisplay="1h 35m"
        impact="All API requests failed" rootCause="Disk full"
        authors={["alice"]}
        timeline={[{ time: "10:00", action: "Alert fired", by: "PagerDuty" }]}
        actionItems={[{ task: "Add monitoring", owner: "alice", priority: "high", due: "Nov 1" }]} />
    );
    expect(container.textContent).toContain("DB Outage");
    expect(container.textContent).toContain("sev1");
    expect(container.textContent).toContain("1h 35m");
    expect(container.textContent).toContain("Disk full");
    expect(container.textContent).toContain("Add monitoring");
    expect(container.textContent).toContain("10:00");
  });
});
