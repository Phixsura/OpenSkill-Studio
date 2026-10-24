import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CommunityDashboard } from "@/components/community-dashboard";

describe("CommunityDashboard", () => {
  it("renders community", () => {
    const { container } = render(
      <CommunityDashboard forumDisplay="2,500" starsDisplay="5,000" forksDisplay="800"
        discordDisplay="3,500" twitterDisplay="12,000" blogPosts={45}
        communityApps={150} communityScore="vibrant" />
    );
    expect(container.textContent).toContain("Community");
    expect(container.textContent).toContain("vibrant");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("GitHub Stars");
    expect(container.textContent).toContain("3,500");
    expect(container.textContent).toContain("150 community apps");
  });
});
