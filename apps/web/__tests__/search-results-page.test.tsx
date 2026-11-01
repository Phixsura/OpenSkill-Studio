import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchResultsPage } from "@/components/search-results-page";

describe("SearchResultsPage", () => {
  it("renders results", () => {
    const onSelect = vi.fn();
    const { container, getAllByRole } = render(
      <SearchResultsPage query="slack" total={2} onSelect={onSelect} results={[
        { id: "app1", name: "Slack Bot", icon: "💬", description: "Chat integration" },
        { id: "app2", name: "Slack Notifier", icon: "🔔", description: "Notifications" },
      ]} />
    );
    expect(container.textContent).toContain("2 results");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Chat integration");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onSelect).toHaveBeenCalledWith("app1");
  });
});
