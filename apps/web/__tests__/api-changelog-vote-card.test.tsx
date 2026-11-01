import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogVoteCard from "../src/components/api-changelog-vote-card";

const entries = [
  { entry_id: "e1", title: "v2.0 Release", score: 15, upvote_count: 18, downvote_count: 3 },
  { entry_id: "e2", title: "Breaking Change", score: -2, upvote_count: 5, downvote_count: 7 },
];

describe("APIChangelogVoteCard", () => {
  it("shows votes", () => {
    const { container } = render(<APIChangelogVoteCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("Changelog Votes");
    expect(container.textContent).toContain("+18");
    expect(container.textContent).toContain("-3");
    expect(container.textContent).toContain("15");
  });
  it("shows empty", () => {
    const { container } = render(<APIChangelogVoteCard entries={[]} appName="App" />);
    expect(container.textContent).toContain("No votes yet");
  });
});
