import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperWelcomeBanner } from "@/components/developer-welcome-banner";

describe("DeveloperWelcomeBanner", () => {
  it("shows welcome for new dev", () => {
    const { container } = render(<DeveloperWelcomeBanner developerName="Alice" appCount={0} isNew={true} />);
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("first app");
  });
  it("shows welcome back", () => {
    const { container } = render(<DeveloperWelcomeBanner developerName="Bob" appCount={5} isNew={false} />);
    expect(container.textContent).toContain("Welcome back");
    expect(container.textContent).toContain("5 apps");
  });
});
