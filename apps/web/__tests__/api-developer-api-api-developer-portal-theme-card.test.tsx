import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperPortalThemeCard from "../src/components/api-developer-api-api-developer-portal-theme-card";

describe("APIDeveloperAPIApiDeveloperPortalThemeCard", () => {
  it("shows theme", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperPortalThemeCard theme={{ primary_color: "#FF5733", secondary_color: "#33FF57", font_family: "Inter", dark_mode: true, portal_title: "My API Portal", has_custom: true }} appName="App" />);
    expect(container.textContent).toContain("Portal Theme");
    expect(container.textContent).toContain("My API Portal");
    expect(container.textContent).toContain("#FF5733");
    expect(container.textContent).toContain("Inter");
    expect(container.textContent).toContain("custom");
  });
});
