import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperProfileHeader } from "@/components/developer-profile-header";

describe("DeveloperProfileHeader", () => {
  it("renders", () => {
    const stats = { total_apps: 5, total_installs: 7000, avg_rating: 4.2 };
    const { container } = render(
      <DeveloperProfileHeader displayName="Alice" bio="Builder" joined="2024-01-01"
        verified={true} stats={stats} />
    );
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Builder");
    expect(container.textContent).toContain("✓ Verified");
    expect(container.textContent).toContain("7,000");
    expect(container.textContent).toContain("⭐ 4.2");
  });
});
