import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CollectionDetailLayout } from "@/components/collection-detail-layout";

describe("CollectionDetailLayout", () => {
  it("renders", () => {
    const { container } = render(
      <CollectionDetailLayout title="Best Tools" description="Top picks" type="editorial"
        appCount={12} curatorName="Team" curatorVerified={true}>
        <p>Apps here</p>
      </CollectionDetailLayout>
    );
    expect(container.textContent).toContain("Best Tools");
    expect(container.textContent).toContain("Top picks");
    expect(container.textContent).toContain("Editorial Pick");
    expect(container.textContent).toContain("12 apps");
    expect(container.textContent).toContain("Team");
    expect(container.textContent).toContain("Apps here");
  });
});
