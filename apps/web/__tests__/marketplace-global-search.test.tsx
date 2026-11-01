import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceGlobalSearch } from "@/components/marketplace-global-search";

const mockResults = [
  { id: "e1", type: "extension" as const, title: "Slack Bot", description: "Slack integration", icon: "💬", meta: "15K installs" },
  { id: "d1", type: "developer" as const, title: "Alice Chen", description: "Full-stack developer", icon: "👩‍💻", meta: "8 extensions" },
  { id: "c1", type: "connector" as const, title: "GitHub Sync", description: "Sync with GitHub", icon: "🐙", meta: "Popular" },
];

describe("MarketplaceGlobalSearch", () => {
  it("renders search input", () => {
    const { getByPlaceholderText } = render(<MarketplaceGlobalSearch results={[]} />);
    expect(getByPlaceholderText("Search extensions, connectors, developers...")).toBeDefined();
  });

  it("calls onSearch when typing", () => {
    const onSearch = vi.fn();
    const { getByPlaceholderText } = render(<MarketplaceGlobalSearch results={[]} onSearch={onSearch} />);
    fireEvent.change(getByPlaceholderText("Search extensions, connectors, developers..."), { target: { value: "slack" } });
    expect(onSearch).toHaveBeenCalledWith("slack");
  });

  it("shows results on focus with query", () => {
    const { container, getByPlaceholderText } = render(
      <MarketplaceGlobalSearch results={mockResults} />
    );
    const input = getByPlaceholderText("Search extensions, connectors, developers...");
    fireEvent.change(input, { target: { value: "slack" } });
    fireEvent.focus(input);
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Alice Chen");
    expect(container.textContent).toContain("extension");
  });

  it("calls onSelect when clicking result", () => {
    const onSelect = vi.fn();
    const { getByPlaceholderText, getByText } = render(
      <MarketplaceGlobalSearch results={mockResults} onSelect={onSelect} />
    );
    fireEvent.change(getByPlaceholderText("Search extensions, connectors, developers..."), { target: { value: "s" } });
    fireEvent.focus(getByPlaceholderText("Search extensions, connectors, developers..."));
    fireEvent.click(getByText("Slack Bot"));
    expect(onSelect).toHaveBeenCalledWith("e1", "extension");
  });
});
