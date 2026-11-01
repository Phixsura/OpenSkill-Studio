import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DiffAnalyzerCard from "../src/components/api-developer-platform-sdk-consumer-api-diff-analyzer-card";

describe("DiffAnalyzerCard", () => {
  it("renders title and diffs", () => {
    const { container } = render(<DiffAnalyzerCard />);
    expect(container.textContent).toContain("API Diff Analyzer");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/orders");
  });

  it("shows breaking changes", () => {
    const { container } = render(<DiffAnalyzerCard />);
    expect(container.textContent).toContain("BREAKING");
    expect(container.textContent).toContain("1 breaking change detected");
  });
});
