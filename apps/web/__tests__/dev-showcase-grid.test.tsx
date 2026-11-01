import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DevShowcaseGrid } from "@/components/dev-showcase-grid";

describe("DevShowcaseGrid", () => {
  it("renders showcase", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <DevShowcaseGrid onSelect={onSelect} developers={[
        { name: "Acme Corp", bio: "Developer tools", appCount: 10,
          installsDisplay: "100,000", verified: true, spotlight: true },
        { name: "Indie Dev", bio: "Solo builder", appCount: 2,
          installsDisplay: "5,000", verified: false, spotlight: false },
      ]} />
    );
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("100,000");
    expect(container.textContent).toContain("10 apps");
    expect(container.textContent).toContain("Indie Dev");
    fireEvent.click(getByText("Acme Corp"));
    expect(onSelect).toHaveBeenCalledWith("Acme Corp");
  });
});
