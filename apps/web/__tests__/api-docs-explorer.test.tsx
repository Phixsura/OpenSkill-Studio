import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiDocsExplorer } from "@/components/api-docs-explorer";

describe("ApiDocsExplorer", () => {
  const sections = [{
    tag: "apps",
    endpoints: [
      { method: "GET", path: "/apps", summary: "List", auth_required: false },
      { method: "POST", path: "/apps", summary: "Create", auth_required: true },
    ],
  }];
  it("renders", () => {
    const { container } = render(
      <ApiDocsExplorer title="MyAPI" version="1.0" sections={sections}
        totalEndpoints={2} onTryIt={vi.fn()} />
    );
    expect(container.textContent).toContain("MyAPI");
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/apps");
    expect(container.textContent).toContain("🔒");
  });
  it("try it", () => {
    const fn = vi.fn();
    const { container } = render(
      <ApiDocsExplorer title="X" version="1" sections={sections} totalEndpoints={2} onTryIt={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Try it")!);
    expect(fn).toHaveBeenCalledWith("GET", "/apps");
  });
});
