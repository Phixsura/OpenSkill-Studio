import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DevPortalHome } from "@/components/dev-portal-home";

describe("DevPortalHome", () => {
  it("renders portal", () => {
    const { container } = render(
      <DevPortalHome progressPct={33} remainingTimeMin={55} developers={5000}
        appsPublished={300} displayCalls="25.0M"
        quickstarts={[
          { id: "sdk-setup", title: "SDK Quick Start", timeMin: 5, category: "setup", completed: true },
          { id: "first-app", title: "Build First App", timeMin: 15, category: "setup", completed: false },
        ]} />
    );
    expect(container.textContent).toContain("Developer Portal");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("300");
    expect(container.textContent).toContain("25.0M");
    expect(container.textContent).toContain("33%");
    expect(container.textContent).toContain("SDK Quick Start");
    expect(container.textContent).toContain("Build First App");
  });
});
