import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiChangelogTimeline } from "@/components/api-changelog-timeline";

describe("ApiChangelogTimeline", () => {
  it("renders changelog", () => {
    const { container } = render(
      <ApiChangelogTimeline totalChanges={3} breakingCount={1}
        versions={{
          "2.0": [
            { type: "added", endpoint: "/users", description: "New", breaking: false },
            { type: "removed", endpoint: "/legacy", description: "Gone", breaking: true },
          ],
          "1.5": [{ type: "fixed", endpoint: "/auth", description: "Fix", breaking: false }],
        }} />
    );
    expect(container.textContent).toContain("API Changelog");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("1 breaking");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("v1.5");
  });
});
