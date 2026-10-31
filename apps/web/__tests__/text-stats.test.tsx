import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TextStats } from "@/components/text-stats";

describe("TextStats", () => {
  it("renders stats", () => {
    const { container } = render(<TextStats words={150} characters={800} sentences={10} readingTimeMin={1} />);
    expect(container.textContent).toContain("150 words");
    expect(container.textContent).toContain("800 chars");
    expect(container.textContent).toContain("10 sentences");
    expect(container.textContent).toContain("~1 min read");
  });
});
