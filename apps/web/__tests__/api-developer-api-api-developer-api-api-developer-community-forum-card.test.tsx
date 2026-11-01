import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForumCard from "../src/components/api-developer-api-api-developer-api-api-developer-community-forum-card";

const posts = [{ post_id: "p1", title: "How to authenticate?", category: "question", status: "open", reply_count: 5, upvotes: 12, author_id: "dev1" }];

describe("Card", () => {
  it("shows forum", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForumCard posts={posts} unansweredCount={3} categoryCounts={{ question: 5 }} appName="App" />);
    expect(container.textContent).toContain("Community Forum");
    expect(container.textContent).toContain("3 unanswered");
    expect(container.textContent).toContain("How to authenticate?");
    expect(container.textContent).toContain("5 replies");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForumCard posts={[]} unansweredCount={0} categoryCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No forum posts");
  });
});
