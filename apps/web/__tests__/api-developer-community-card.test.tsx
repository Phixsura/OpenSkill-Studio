import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperCommunityCard from "../src/components/api-developer-community-card";

const discussions = [
  { discussion_id: "d1", title: "Auth help", author: "alice", reply_count: 5, resolved: false },
  { discussion_id: "d2", title: "SDK error", author: "bob", reply_count: 3, resolved: true },
];

describe("APIDeveloperCommunityCard", () => {
  it("shows discussions", () => {
    const { container } = render(<APIDeveloperCommunityCard discussions={discussions} appName="App" />);
    expect(container.textContent).toContain("Community");
    expect(container.textContent).toContain("1 open / 2 total");
    expect(container.textContent).toContain("Auth help");
    expect(container.textContent).toContain("5 replies");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperCommunityCard discussions={[]} appName="App" />);
    expect(container.textContent).toContain("No discussions");
  });
});
