import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppRecommendations } from "@/components/app-recommendations";

describe("AppRecommendations", () => {
  it("renders recs", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <AppRecommendations title="Recommended for You" onSelect={onSelect} apps={[
        { id: "a1", name: "Slack Bot", icon: "💬", rating: 4.8, reason: "Popular in comm" },
        { id: "a2", name: "GitHub Sync", icon: "🐙", rating: 4.5 },
      ]} />
    );
    expect(container.textContent).toContain("Recommended for You");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("4.8");
    expect(container.textContent).toContain("Popular in comm");
    fireEvent.click(getByText("Slack Bot"));
    expect(onSelect).toHaveBeenCalledWith("a1");
  });
});
