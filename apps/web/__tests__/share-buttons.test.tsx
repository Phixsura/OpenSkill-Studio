import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ShareButtons } from "@/components/share-buttons";

describe("ShareButtons", () => {
  it("shows all buttons", () => {
    const { container } = render(<ShareButtons url="u" twitter="t" linkedin="l" email="e" copyText="c" />);
    expect(container.textContent).toContain("Tweet");
    expect(container.textContent).toContain("Share");
    expect(container.textContent).toContain("Email");
    expect(container.textContent).toContain("Copy");
  });
  it("has links", () => {
    const { container } = render(<ShareButtons url="u" twitter="https://t.co" linkedin="https://li.com" email="mailto:x" copyText="c" />);
    expect(container.querySelectorAll("a").length).toBe(3);
  });
});
