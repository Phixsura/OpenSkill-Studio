import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperSpotlightCard } from "@/components/developer-spotlight-card";

describe("DeveloperSpotlightCard", () => {
  it("renders card", () => {
    const { container } = render(
      <DeveloperSpotlightCard name="DevCo" slug="devco" bio="We build tools" verified={true} avatarInitial="D"
        stats={{ apps: 5, installs: 2000, rating: 4.5 }} topApps={[{ name: "App1", slug: "app1" }]} />
    );
    expect(container.textContent).toContain("DevCo");
    expect(container.textContent).toContain("2,000");
    expect(container.textContent).toContain("4.5 ★");
    expect(container.textContent).toContain("App1");
    expect(container.querySelector("a")?.getAttribute("href")).toBe("/marketplace/developers/devco");
  });
});
