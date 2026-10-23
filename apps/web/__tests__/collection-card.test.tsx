import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CollectionCard } from "@/components/collection-card";

describe("CollectionCard", () => {
  it("renders collection", () => {
    const { container } = render(
      <CollectionCard title="Best Tools" description="Top tools" curator="Alice"
        appCount={5} featured={true} onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Best Tools");
    expect(container.textContent).toContain("Top tools");
    expect(container.textContent).toContain("by Alice");
    expect(container.textContent).toContain("5 apps");
    expect(container.textContent).toContain("Featured");
  });
});
