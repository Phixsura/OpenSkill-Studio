import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogMentionCard from "../src/components/changelog-mention-card";

const mentions = [
  { version: "2.0.0", users: ["alice"], issues: [42, 55], prs: [15] },
  { version: "1.0.0", users: ["alice", "bob"], issues: [42], prs: [10] },
];

describe("ChangelogMentionCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ChangelogMentionCard mentions={mentions} appName="My App" />);
    expect(container.textContent).toContain("Mentions");
    expect(container.textContent).toContain("My App");
  });

  it("shows contributor and issue counts", () => {
    const { container } = render(<ChangelogMentionCard mentions={mentions} appName="App" />);
    expect(container.textContent).toContain("2 contributors");
    expect(container.textContent).toContain("2 issues");
  });

  it("renders version labels", () => {
    const { container } = render(<ChangelogMentionCard mentions={mentions} appName="App" />);
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("v1.0.0");
  });

  it("shows user mentions", () => {
    const { container } = render(<ChangelogMentionCard mentions={mentions} appName="App" />);
    expect(container.textContent).toContain("@alice");
    expect(container.textContent).toContain("@bob");
  });

  it("shows issue references", () => {
    const { container } = render(<ChangelogMentionCard mentions={mentions} appName="App" />);
    expect(container.textContent).toContain("#42");
    expect(container.textContent).toContain("#55");
  });

  it("shows PR references", () => {
    const { container } = render(<ChangelogMentionCard mentions={mentions} appName="App" />);
    expect(container.textContent).toContain("PR #15");
    expect(container.textContent).toContain("PR #10");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogMentionCard mentions={[]} appName="App" />);
    expect(container.textContent).toContain("No mentions found");
  });
});
