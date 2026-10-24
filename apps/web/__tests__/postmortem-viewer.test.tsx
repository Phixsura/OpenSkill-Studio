import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PostmortemViewer } from "@/components/postmortem-viewer";

describe("PostmortemViewer", () => {
  it("renders", () => {
    const { container } = render(
      <PostmortemViewer title="API Outage" severity="critical" durationMinutes={30}
        usersAffected={5000} rootCause="Connection pool exhausted"
        actionItems={["Increase pool size", "Add monitoring"]} status="completed" />
    );
    expect(container.textContent).toContain("API Outage");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("30min");
    expect(container.textContent).toContain("5,000 users");
    expect(container.textContent).toContain("Connection pool exhausted");
    expect(container.textContent).toContain("Increase pool size");
  });
});
