import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogEmbedCard from "../src/components/api-changelog-embed-card";

describe("APIChangelogEmbedCard", () => {
  it("shows config", () => {
    const { container } = render(<APIChangelogEmbedCard config={{ theme: "dark", max_entries: 10, show_reactions: true }} appName="App" />);
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("on");
  });
});
