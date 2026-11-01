import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DevProfileCard } from "@/components/dev-profile-card";

describe("DevProfileCard", () => {
  it("renders profile", () => {
    const { container } = render(
      <DevProfileCard name="Acme Corp" bio="Developer tools" verified={true}
        joined="2024-01-01" appCount={2} totalInstallsDisplay="80,000"
        avgRating={4.65} apps={[
          { name: "Slack Bot", icon: "💬", rating: 4.8, installs: 50000 },
        ]} />
    );
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("Developer tools");
    expect(container.textContent).toContain("80,000 installs");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("4.8");
    expect(container.textContent).toContain("2024-01-01");
  });
});
