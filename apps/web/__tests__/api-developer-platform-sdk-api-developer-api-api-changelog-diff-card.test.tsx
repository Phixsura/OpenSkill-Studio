import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiffCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-changelog-diff-card";

const diffs = [{
  from_version: "v1", to_version: "v2",
  changes: [{ change_type: "added", target: "GET /api/v2/users", description: "New" }, { change_type: "removed", target: "GET /api/v1/users", description: "Old" }],
  breaking_count: 1, additions: 1, is_breaking: true,
}];

describe("Card", () => {
  it("shows changelog diff", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiffCard diffs={diffs} appName="App" />);
    expect(container.textContent).toContain("Changelog Diff");
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("breaking");
    expect(container.textContent).toContain("GET /api/v2/users");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiffCard diffs={[]} appName="App" />);
    expect(container.textContent).toContain("No diffs");
  });
});
