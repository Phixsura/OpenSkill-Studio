import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppStoreCard } from "@/components/app-store-card";

describe("AppStoreCard", () => {
  it("renders app listing", () => {
    const { container } = render(
      <AppStoreCard name="SuperApp" shortDescription="A great app" icon="🚀"
        category="Productivity" version="2.1.0" author="Alice" downloads={15000}
        avgRating={4.7} starsDisplay="★★★★☆" reviewCount={42} pricing="$9/mo"
        verified={true} tags={["productivity", "teams"]} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("A great app");
    expect(container.textContent).toContain("★★★★☆");
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("$9/mo");
    expect(container.textContent).toContain("productivity");
    expect(container.textContent).toContain("✓"); // verified
  });
});
