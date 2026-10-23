import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperProfileCard } from "@/components/developer-profile-card";

describe("DeveloperProfileCard", () => {
  it("renders profile", () => {
    const { container } = render(
      <DeveloperProfileCard name="Alice" bio="Building great apps"
        avatarUrl="https://example.com/avatar.png" appsCount={10}
        downloadsDisplay="250K" verified={true} badge="🏆 Top Publisher"
        links={{ github: "https://github.com/alice" }} />
    );
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Building great apps");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("250K");
    expect(container.textContent).toContain("Top Publisher");
    expect(container.textContent).toContain("github");
  });
});
