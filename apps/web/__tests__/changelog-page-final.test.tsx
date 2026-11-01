import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogPageFinal } from "@/components/changelog-page-final";

describe("ChangelogPageFinal", () => {
  const entries = [
    { title: "Platform v3.0", date: "2026-10-20", entry_type: "platform" },
    { title: "App SDK v2", date: "2026-10-21", entry_type: "app" },
  ];
  it("renders", () => {
    const { container } = render(
      <ChangelogPageFinal entries={entries} filterOptions={["all", "platform", "app"]}
        activeFilter="all" onFilterChange={vi.fn()} rssUrl="/feed.rss" />
    );
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("Platform v3.0");
    expect(container.textContent).toContain("App SDK v2");
    expect(container.textContent).toContain("RSS");
  });
  it("filters", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChangelogPageFinal entries={entries} filterOptions={["all", "platform"]}
        activeFilter="all" onFilterChange={fn} rssUrl="" />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "platform")!);
    expect(fn).toHaveBeenCalledWith("platform");
  });
});
