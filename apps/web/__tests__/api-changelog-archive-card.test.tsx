import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogArchiveCard from "../src/components/api-changelog-archive-card";

const entries = [
  { entry_id: "e1", title: "v1 Release", version: "v1", archived: true },
  { entry_id: "e2", title: "v2 Release", version: "v2", archived: false },
];

describe("APIChangelogArchiveCard", () => {
  it("shows counts and entries", () => {
    const { container } = render(<APIChangelogArchiveCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("1 archived");
    expect(container.textContent).toContain("v1 Release");
  });
  it("shows empty", () => {
    const { container } = render(<APIChangelogArchiveCard entries={[]} appName="App" />);
    expect(container.textContent).toContain("No entries");
  });
});
