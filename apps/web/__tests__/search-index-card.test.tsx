import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SearchIndexCard from "../src/components/search-index-card";

const docTypes = [
  { type: "user", count: 150 },
  { type: "project", count: 45 },
];
const searches = [
  { query: "alice", hits: 3 },
  { query: "api endpoint", hits: 12 },
];

describe("SearchIndexCard", () => {
  it("renders header", () => {
    const { container } = render(
      <SearchIndexCard
        docCount={195}
        docTypes={docTypes}
        recentSearches={searches}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Search Index");
  });

  it("shows document count", () => {
    const { container } = render(
      <SearchIndexCard docCount={195} docTypes={docTypes} recentSearches={[]} appName="App" />,
    );
    expect(container.textContent).toContain("195 documents");
  });

  it("renders doc types", () => {
    const { container } = render(
      <SearchIndexCard docCount={195} docTypes={docTypes} recentSearches={[]} appName="App" />,
    );
    expect(container.textContent).toContain("user (150)");
    expect(container.textContent).toContain("project (45)");
  });

  it("renders recent searches", () => {
    const { container } = render(
      <SearchIndexCard docCount={0} docTypes={[]} recentSearches={searches} appName="App" />,
    );
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("3 hits");
  });

  it("shows empty state", () => {
    const { container } = render(
      <SearchIndexCard docCount={0} docTypes={[]} recentSearches={[]} appName="App" />,
    );
    expect(container.textContent).toContain("Empty index");
  });
});
