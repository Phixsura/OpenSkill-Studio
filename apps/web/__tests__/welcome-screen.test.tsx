import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WelcomeScreen } from "@/components/welcome-screen";

const props = {
  greeting: "Welcome back, Alice!", displayName: "Alice",
  extensionsCount: 5, totalInstalls: 10000, unreadNotifications: 3,
  recentActivity: ["Deployed v2.0", "New review received"],
  suggestedActions: ["Optimize listing", "Apply for verification"],
  onboardingComplete: true,
};

describe("WelcomeScreen", () => {
  it("renders welcome screen", () => {
    const { container } = render(<WelcomeScreen {...props} />);
    expect(container.textContent).toContain("Welcome back, Alice!");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("Optimize listing");
    expect(container.textContent).toContain("Deployed v2.0");
  });
});
