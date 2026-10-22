import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceReadinessCard } from "@/components/marketplace-readiness-card";

describe("MarketplaceReadinessCard", () => {
  it("shows ready", () => {
    const { container } = render(<MarketplaceReadinessCard ready={true} errors={[]} warnings={[]} />);
    expect(container.textContent).toContain("Ready");
    expect(container.textContent).toContain("All checks");
  });
  it("shows errors", () => {
    const { container } = render(<MarketplaceReadinessCard ready={false} errors={["Missing description"]} warnings={[]} />);
    expect(container.textContent).toContain("Missing description");
  });
  it("shows warnings", () => {
    const { container } = render(<MarketplaceReadinessCard ready={true} errors={[]} warnings={["Add icon"]} />);
    expect(container.textContent).toContain("Add icon");
  });
});
