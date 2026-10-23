import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiChangelogTimeline } from "@/components/api-changelog-timeline";

describe("ApiChangelogTimeline", () => {
  it("renders changelog", () => {
    const { container } = render(
      <ApiChangelogTimeline totalChanges={3} severity="major" sections={[
        { type: "breaking", count: 1, entries: [{ endpoint: "/api/v1/users", description: "Removed email", version: "3.0", date: "" }] },
        { type: "added", count: 1, entries: [{ endpoint: "/api/v1/exports", description: "New export", version: "3.0", date: "" }] },
      ]} />
    );
    expect(container.textContent).toContain("API Changelog");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("major");
    expect(container.textContent).toContain("Breaking Changes");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("New Endpoints");
  });
});
