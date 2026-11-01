import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogDiffCard from "../src/components/api-changelog-diff-card";

const diffs = [
  { diff_id: "d1", from_version: "v1", to_version: "v2", change_count: 3, summary: { added: 1, removed: 1, modified: 1 } },
];

describe("APIChangelogDiffCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIChangelogDiffCard diffs={diffs} appName="App" />);
    expect(container.textContent).toContain("Changelog Diffs");
    expect(container.textContent).toContain("1 diffs");
  });

  it("shows version transition and changes", () => {
    const { container } = render(<APIChangelogDiffCard diffs={diffs} appName="App" />);
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("3 changes");
  });

  it("shows diff stats", () => {
    const { container } = render(<APIChangelogDiffCard diffs={diffs} appName="App" />);
    expect(container.textContent).toContain("+1");
    expect(container.textContent).toContain("-1");
    expect(container.textContent).toContain("~1");
  });

  it("shows empty state", () => {
    const { container } = render(<APIChangelogDiffCard diffs={[]} appName="App" />);
    expect(container.textContent).toContain("No version diffs");
  });
});
