import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogCommentCard from "../src/components/api-changelog-comment-card";

const comments = [
  { comment_id: "c1", author: "alice", body: "Great update!", parent_id: null },
  { comment_id: "c2", author: "bob", body: "Thanks!", parent_id: "c1" },
];

describe("APIChangelogCommentCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIChangelogCommentCard comments={comments} entryTitle="v2.0" appName="App" />);
    expect(container.textContent).toContain("Comments");
    expect(container.textContent).toContain("2 comments");
  });

  it("shows authors and bodies", () => {
    const { container } = render(<APIChangelogCommentCard comments={comments} entryTitle="v2.0" appName="App" />);
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("Great update!");
    expect(container.textContent).toContain("bob");
  });

  it("shows empty state", () => {
    const { container } = render(<APIChangelogCommentCard comments={[]} entryTitle="v1" appName="App" />);
    expect(container.textContent).toContain("No comments");
  });
});
