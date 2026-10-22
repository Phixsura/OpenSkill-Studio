import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigDiffViewer } from "@/components/config-diff-viewer";

describe("ConfigDiffViewer", () => {
  it("shows no changes", () => {
    const { container } = render(<ConfigDiffViewer added={{}} removed={{}} changed={{}} />);
    expect(container.textContent).toContain("No config changes");
  });

  it("shows added", () => {
    const { container } = render(<ConfigDiffViewer added={{ url: "https://x.com" }} removed={{}} changed={{}} />);
    expect(container.textContent).toContain("url");
    expect(container.textContent).toContain("+");
  });

  it("shows removed", () => {
    const { container } = render(<ConfigDiffViewer added={{}} removed={{ old_key: "val" }} changed={{}} />);
    expect(container.textContent).toContain("old_key");
  });

  it("shows changed", () => {
    const { container } = render(<ConfigDiffViewer added={{}} removed={{}} changed={{ timeout: { from: 30, to: 60 } }} />);
    expect(container.textContent).toContain("30");
    expect(container.textContent).toContain("60");
  });
});
