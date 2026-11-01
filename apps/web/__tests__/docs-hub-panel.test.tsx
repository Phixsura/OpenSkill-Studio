import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DocsHubPanel } from "@/components/docs-hub-panel";

const docs = [
  { slug: "quickstart", title: "Quick Start", category: "guide", read: true },
  { slug: "auth", title: "Authentication", category: "security", read: false },
];
const progress = { read: 1, total: 2, percent: 50 };

describe("DocsHubPanel", () => {
  it("renders docs", () => {
    const { container } = render(<DocsHubPanel docs={docs} progress={progress} categories={["guide", "security"]} />);
    expect(container.textContent).toContain("Quick Start");
    expect(container.textContent).toContain("50% read");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { getByText } = render(<DocsHubPanel docs={docs} progress={progress} categories={[]} onSelect={fn} />);
    fireEvent.click(getByText("Authentication"));
    expect(fn).toHaveBeenCalledWith("auth");
  });
});
