import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceSearch } from "@/components/marketplace-search";

const MOCK_RESPONSE = {
  results: [
    {
      app: {
        app_id: "app-1",
        name: "LMS Connector",
        description: "Sync grades and courses",
        category: "connector",
        icon: "🔗",
        publisher: "EduTech",
        rating: 4.5,
        downloads: 1200,
        price_tier: "free" as const,
        tags: ["lms", "grades", "sync"],
      },
      score: 3.2,
      highlights: ["lms", "sync"],
    },
    {
      app: {
        app_id: "app-2",
        name: "AI Rubric",
        description: "Generate rubrics with AI",
        category: "evaluation",
        icon: "🤖",
        publisher: "AITools",
        rating: 4.8,
        downloads: 800,
        price_tier: "paid" as const,
        tags: ["ai", "rubric"],
      },
      score: 2.1,
      highlights: [],
    },
  ],
  total: 42,
  page: 1,
  per_page: 20,
  has_more: true,
  facets: {
    category: { connector: 5, evaluation: 3, analytics: 2 },
    price_tier: { free: 4, paid: 3 },
  },
};

const defaultProps = {
  response: MOCK_RESPONSE,
  query: "lms",
  onQueryChange: vi.fn(),
  onSearch: vi.fn(),
  onCategoryFilter: vi.fn(),
  onInstall: vi.fn(),
  onLoadMore: vi.fn(),
  activeCategory: null as string | null,
};

describe("MarketplaceSearch", () => {
  it("renders search input with query", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    const input = container.querySelector(
      "input[aria-label='Search marketplace']",
    ) as HTMLInputElement;
    expect(input).toBeTruthy();
    expect(input.value).toBe("lms");
  });

  it("renders result count", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    expect(container.textContent).toContain("42 results found");
  });

  it("renders app names", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    expect(container.textContent).toContain("LMS Connector");
    expect(container.textContent).toContain("AI Rubric");
  });

  it("renders price tier badges", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("Paid");
  });

  it("renders star ratings", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("4.8");
  });

  it("renders download counts", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    expect(container.textContent).toContain("1,200 downloads");
  });

  it("renders category facet buttons", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    expect(container.textContent).toContain("connector (5)");
    expect(container.textContent).toContain("evaluation (3)");
    expect(container.textContent).toContain("All");
  });

  it("calls onCategoryFilter when facet clicked", () => {
    const onCategoryFilter = vi.fn();
    const { container } = render(
      <MarketplaceSearch {...defaultProps} onCategoryFilter={onCategoryFilter} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("connector"),
    );
    fireEvent.click(btn!);
    expect(onCategoryFilter).toHaveBeenCalledWith("connector");
  });

  it("calls onInstall when Install clicked", () => {
    const onInstall = vi.fn();
    const { container } = render(<MarketplaceSearch {...defaultProps} onInstall={onInstall} />);
    const installBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Install",
    );
    fireEvent.click(installBtns[0]);
    expect(onInstall).toHaveBeenCalledWith("app-1");
  });

  it("calls onSearch on Enter key", () => {
    const onSearch = vi.fn();
    const { container } = render(<MarketplaceSearch {...defaultProps} onSearch={onSearch} />);
    const input = container.querySelector("input")!;
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onSearch).toHaveBeenCalledOnce();
  });

  it("shows Load more when has_more", () => {
    const onLoadMore = vi.fn();
    const { container } = render(<MarketplaceSearch {...defaultProps} onLoadMore={onLoadMore} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Load more",
    );
    expect(btn).toBeTruthy();
    fireEvent.click(btn!);
    expect(onLoadMore).toHaveBeenCalledOnce();
  });

  it("hides Load more when no more results", () => {
    const noMore = { ...MOCK_RESPONSE, has_more: false };
    const { container } = render(<MarketplaceSearch {...defaultProps} response={noMore} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Load more",
    );
    expect(btn).toBeFalsy();
  });

  it("shows empty state", () => {
    const empty = { ...MOCK_RESPONSE, results: [], total: 0 };
    const { container } = render(<MarketplaceSearch {...defaultProps} response={empty} />);
    expect(container.textContent).toContain("No apps found");
  });

  it("renders tags with highlight", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    // "lms" and "sync" are highlights for app-1
    expect(container.textContent).toContain("lms");
    expect(container.textContent).toContain("sync");
  });

  it("renders publisher names", () => {
    const { container } = render(<MarketplaceSearch {...defaultProps} />);
    expect(container.textContent).toContain("by EduTech");
    expect(container.textContent).toContain("by AITools");
  });
});
