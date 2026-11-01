import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppChangelogView } from "@/components/app-changelog-view";

describe("AppChangelogView", () => {
  it("renders changelog", () => {
    const { container } = render(
      <AppChangelogView totalChanges={3} versions={[
        { version: "2.0.0", date: "2026-10-24", summary: "Major", changeCount: 2,
          changes: [{ type: "added", icon: "✨", text: "SSO" }, { type: "fixed", icon: "🐛", text: "Bug fix" }] },
      ]} />
    );
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("SSO");
    expect(container.textContent).toContain("Bug fix");
    expect(container.textContent).toContain("3 changes");
  });
});
