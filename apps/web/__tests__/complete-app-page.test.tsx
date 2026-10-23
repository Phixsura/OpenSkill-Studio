import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CompleteAppPage } from "@/components/complete-app-page";

describe("CompleteAppPage", () => {
  it("renders page", () => {
    const onInstall = vi.fn();
    const { container, getByText } = render(
      <CompleteAppPage heroName="Slack Bot" heroIcon="💬" heroTagline="Best Slack"
        heroDeveloper="Acme" activeTab="overview" priceDisplay="Free"
        onTabChange={vi.fn()} onInstall={onInstall}
        tabs={[{ id: "overview", label: "Overview", icon: "📋" }, { id: "reviews", label: "Reviews", icon: "⭐" }]}>
        <p>Tab content</p>
      </CompleteAppPage>
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Best Slack");
    expect(container.textContent).toContain("Acme");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Tab content");
    fireEvent.click(getByText("Install"));
    expect(onInstall).toHaveBeenCalled();
  });
});
