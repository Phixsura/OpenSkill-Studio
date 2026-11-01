import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogSearchCard from "../src/components/changelog-search-card";

const results = [
  {
    entry_id: "e1",
    version: "2.0.0",
    title: "New dashboard API",
    category: "added",
    score: 4,
    matched_fields: ["title", "description"],
  },
  {
    entry_id: "e2",
    version: "1.0.0",
    title: "Initial release",
    category: "added",
    score: 1,
    matched_fields: ["description"],
  },
];

describe("ChangelogSearchCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <ChangelogSearchCard query="API" results={results} totalIndexed={50} appName="My App" />,
    );
    expect(container.textContent).toContain("Changelog Search");
    expect(container.textContent).toContain("My App");
  });

  it("shows indexed count", () => {
    const { container } = render(
      <ChangelogSearchCard query="" results={[]} totalIndexed={50} appName="App" />,
    );
    expect(container.textContent).toContain("50 entries indexed");
  });

  it("shows result count and query", () => {
    const { container } = render(
      <ChangelogSearchCard query="API" results={results} totalIndexed={50} appName="App" />,
    );
    expect(container.textContent).toContain("2 results for");
    expect(container.textContent).toContain("API");
  });

  it("renders result titles and versions", () => {
    const { container } = render(
      <ChangelogSearchCard query="API" results={results} totalIndexed={50} appName="App" />,
    );
    expect(container.textContent).toContain("New dashboard API");
    expect(container.textContent).toContain("v2.0.0");
  });

  it("shows matched fields", () => {
    const { container } = render(
      <ChangelogSearchCard query="API" results={results} totalIndexed={50} appName="App" />,
    );
    expect(container.textContent).toContain("title, description");
  });

  it("shows no-results message", () => {
    const { container } = render(
      <ChangelogSearchCard query="xyz" results={[]} totalIndexed={50} appName="App" />,
    );
    expect(container.textContent).toContain("No results found");
  });

  it("shows prompt when no query", () => {
    const { container } = render(
      <ChangelogSearchCard query="" results={[]} totalIndexed={50} appName="App" />,
    );
    expect(container.textContent).toContain("Enter a search query");
  });
});
