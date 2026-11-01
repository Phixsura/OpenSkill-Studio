import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CollectionPageHeader } from "@/components/collection-page-header";

describe("CollectionPageHeader", () => {
  it("renders header", () => {
    const { container } = render(
      <CollectionPageHeader title="Best Tools" description="Our top picks" appCount={12}
        collectionType="editorial" curatorName="Team" />
    );
    expect(container.textContent).toContain("Best Tools");
    expect(container.textContent).toContain("Our top picks");
    expect(container.textContent).toContain("12 apps");
    expect(container.textContent).toContain("Editorial Pick");
    expect(container.textContent).toContain("Curated by Team");
  });
});
