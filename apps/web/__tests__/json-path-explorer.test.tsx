import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { JsonPathExplorer } from "@/components/json-path-explorer";

describe("JsonPathExplorer", () => {
  it("renders input", () => {
    const { container } = render(<JsonPathExplorer onQuery={vi.fn(() => ({ found: false }))} />);
    expect(container.textContent).toContain("JSONPath Explorer");
    expect(container.querySelector("input")).toBeTruthy();
  });
});
