import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchAutocomplete } from "@/components/search-autocomplete";

describe("SearchAutocomplete", () => {
  it("renders suggestions", () => {
    const onSelect = vi.fn();
    const { container, getAllByRole } = render(
      <SearchAutocomplete visible={true} onSelect={onSelect} suggestions={[
        { text: "Slack Bot", type: "app", icon: "📱" },
        { text: "Slack Inc", type: "developer", icon: "👩‍💻" },
      ]} />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("app");
    expect(container.textContent).toContain("Slack Inc");
    expect(container.textContent).toContain("developer");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onSelect).toHaveBeenCalledWith("Slack Bot");
  });

  it("hides when not visible", () => {
    const { container } = render(
      <SearchAutocomplete visible={false} onSelect={vi.fn()} suggestions={[{ text: "A", type: "app", icon: "" }]} />
    );
    expect(container.textContent).toBe("");
  });
});
