import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogSearchCard from "../src/components/api-changelog-search-card";

const results = [
  { entry_id: "e1", title: "Dark Mode", version: "v2.0", score: 15 },
  { entry_id: "e2", title: "Auth Update", version: "v1.5", score: 5 },
];

describe("APIChangelogSearchCard", () => {
  it("renders header and indexed count", () => {
    const { container } = render(<APIChangelogSearchCard results={results} query="dark" totalIndexed={50} appName="App" />);
    expect(container.textContent).toContain("Changelog Search");
    expect(container.textContent).toContain("50 indexed");
  });

  it("shows query and results", () => {
    const { container } = render(<APIChangelogSearchCard results={results} query="dark" totalIndexed={50} appName="App" />);
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("v2.0");
  });

  it("shows no matches", () => {
    const { container } = render(<APIChangelogSearchCard results={[]} query="xyz" totalIndexed={50} appName="App" />);
    expect(container.textContent).toContain("No matches");
  });
});
