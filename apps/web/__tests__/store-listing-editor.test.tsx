import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StoreListingEditor } from "@/components/store-listing-editor";

describe("StoreListingEditor", () => {
  it("renders listing", () => {
    const { container } = render(
      <StoreListingEditor name="My App" tagline="Best app" description="Long desc"
        category="productivity" pricing="free" completenessPct={80}
        readyToPublish={true} features={["auth", "api"]}
        issues={[]} onPublish={vi.fn()} />
    );
    expect(container.textContent).toContain("Store Listing");
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("Best app");
    expect(container.textContent).toContain("80% complete");
    expect(container.textContent).toContain("Publish");
    expect(container.textContent).toContain("productivity");
  });
});
