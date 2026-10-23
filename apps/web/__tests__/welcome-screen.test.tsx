import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WelcomeScreen } from "@/components/welcome-screen";

describe("WelcomeScreen", () => {
  const features = [{ title: "Easy Setup", description: "Get started", icon: "⚡" }];
  const nextSteps = [{ title: "Docs", href: "/docs", icon: "📖" }];
  it("renders welcome", () => {
    const { container } = render(
      <WelcomeScreen appName="SuperApp" appIcon="🚀" headline="Welcome to SuperApp! 🎉"
        features={features} nextSteps={nextSteps} onDismiss={vi.fn()} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("Welcome to SuperApp!");
    expect(container.textContent).toContain("Easy Setup");
    expect(container.textContent).toContain("Docs");
    expect(container.textContent).toContain("Skip for now");
  });
});
