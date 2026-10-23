import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CommunityPage } from "@/components/community-page";

describe("CommunityPage", () => {
  const links = [{ id: "discord", name: "Discord", icon: "💬", href: "#", members: 5200 }];
  it("renders community", () => {
    const { container } = render(
      <CommunityPage links={links} discussions={[{ title: "Help?", author: "A", replies: 3 }]}
        contributors={[{ name: "Bob", contributions: 42, badge: "🏆" }]} totalMembers={19600} />
    );
    expect(container.textContent).toContain("Developer Community");
    expect(container.textContent).toContain("19,600");
    expect(container.textContent).toContain("Discord");
    expect(container.textContent).toContain("Help?");
    expect(container.textContent).toContain("Bob");
  });
});
