import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogReactionCard from "../src/components/api-changelog-reaction-card";

const entries = [
  { entry_id: "e1", title: "v2.0 Release", counts: { "🚀": 10, "🎉": 5 }, total: 15 },
  { entry_id: "e2", title: "Bug Fix", counts: { "👍": 3 }, total: 3 },
];

describe("APIChangelogReactionCard", () => {
  it("renders header and total", () => {
    const { container } = render(<APIChangelogReactionCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("Changelog Reactions");
    expect(container.textContent).toContain("18 reactions");
  });

  it("shows entries with emoji counts", () => {
    const { container } = render(<APIChangelogReactionCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("v2.0 Release");
    expect(container.textContent).toContain("🚀 10");
    expect(container.textContent).toContain("🎉 5");
  });

  it("shows empty state", () => {
    const { container } = render(<APIChangelogReactionCard entries={[]} appName="App" />);
    expect(container.textContent).toContain("No reactions yet");
  });
});
