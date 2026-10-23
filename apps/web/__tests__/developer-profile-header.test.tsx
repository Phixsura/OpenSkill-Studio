import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperProfileHeader } from "@/components/developer-profile-header";

describe("DeveloperProfileHeader", () => {
  it("renders profile", () => {
    const { container } = render(
      <DeveloperProfileHeader name="DevCo" bio="We build tools" verified={true} joinedAt="2024-01-01"
        totalApps={5} totalInstalls={2500} avgRating={4.5} badges={[{ type: "verified", label: "Verified", icon: "✅" }]} />
    );
    expect(container.textContent).toContain("DevCo");
    expect(container.textContent).toContain("We build tools");
    expect(container.textContent).toContain("2,500");
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("Verified");
  });
});
