import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CollectionCard } from "@/components/collection-card";

describe("CollectionCard", () => {
  it("shows title and description", () => {
    const { container } = render(<CollectionCard title="Best Apps" description="Top rated" appCount={10} slug="best" />);
    expect(container.textContent).toContain("Best Apps");
    expect(container.textContent).toContain("Top rated");
  });
  it("shows app count", () => {
    const { container } = render(<CollectionCard title="X" description="Y" appCount={42} slug="x" />);
    expect(container.textContent).toContain("42 apps");
  });
  it("has link", () => {
    const { container } = render(<CollectionCard title="X" description="Y" appCount={0} slug="my-collection" />);
    expect(container.querySelector("a")?.getAttribute("href")).toContain("my-collection");
  });
});
