import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogWidget } from "@/components/changelog-widget";

describe("ChangelogWidget", () => {
  it("renders widget", () => {
    const onViewAll = vi.fn();
    const { container, getByText } = render(
      <ChangelogWidget hasMore={true} onViewAll={onViewAll} items={[
        { version: "3.5", title: "SSO Support", type: "added", date: "2026-10-24" },
        { version: "3.4.1", title: "Bug fix", type: "fixed", date: "2026-10-20" },
      ]} />
    );
    expect(container.textContent).toContain("What's New");
    expect(container.textContent).toContain("SSO Support");
    expect(container.textContent).toContain("Bug fix");
    fireEvent.click(getByText("View all changes →"));
    expect(onViewAll).toHaveBeenCalled();
  });
});
