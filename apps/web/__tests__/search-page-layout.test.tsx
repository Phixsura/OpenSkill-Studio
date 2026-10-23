import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SearchPageLayout } from "@/components/search-page-layout";

describe("SearchPageLayout", () => {
  it("renders results", () => {
    const { container } = render(
      <SearchPageLayout query="webhook" resultCount={50} empty={false} suggestions={[]} tips={[]}>
        <p>Results here</p>
      </SearchPageLayout>
    );
    expect(container.textContent).toContain('Results for "webhook"');
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("Results here");
  });
  it("renders empty state", () => {
    const { container } = render(
      <SearchPageLayout query="xyz" resultCount={0} empty={true} suggestions={["xyx"]} tips={["Check spelling"]}>
        <p>Hidden</p>
      </SearchPageLayout>
    );
    expect(container.textContent).toContain('No results for "xyz"');
    expect(container.textContent).toContain("Check spelling");
    expect(container.textContent).toContain("xyx");
    expect(container.textContent).not.toContain("Hidden");
  });
});
