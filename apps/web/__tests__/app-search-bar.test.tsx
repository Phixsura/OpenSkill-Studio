import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSearchBar } from "@/components/app-search-bar";

describe("AppSearchBar", () => {
  it("renders input", () => {
    const { container } = render(<AppSearchBar onSearch={vi.fn()} />);
    expect(container.querySelector("input")).toBeTruthy();
  });

  it("renders search button", () => {
    const { container } = render(<AppSearchBar onSearch={vi.fn()} />);
    expect(container.querySelector("button")?.textContent).toContain("Search");
  });

  it("renders category select", () => {
    const { container } = render(<AppSearchBar onSearch={vi.fn()} onCategoryChange={vi.fn()} categories={["connector", "automation"]} />);
    expect(container.querySelector("select")).toBeTruthy();
  });

  it("calls onSearch on submit", () => {
    const onSearch = vi.fn();
    const { container } = render(<AppSearchBar onSearch={onSearch} />);
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "test query" } });
    fireEvent.submit(container.querySelector("form")!);
    expect(onSearch).toHaveBeenCalledWith("test query");
  });

  it("custom placeholder", () => {
    const { container } = render(<AppSearchBar onSearch={vi.fn()} placeholder="Find apps..." />);
    expect(container.querySelector("input")?.placeholder).toBe("Find apps...");
  });
});
