import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CacheControlInspector } from "@/components/cache-control-inspector";

describe("CacheControlInspector", () => {
  const headers = { ETag: '"abc"', "Cache-Control": "public, max-age=300", Expires: "Thu, 23 Oct 2026", Vary: "Accept-Encoding" };
  it("renders", () => {
    const { container } = render(
      <CacheControlInspector headers={headers} hitRate={92} onPurge={vi.fn()} />
    );
    expect(container.textContent).toContain("Cache Inspector");
    expect(container.textContent).toContain("92%");
    expect(container.textContent).toContain("ETag");
    expect(container.textContent).toContain("Cache-Control");
    expect(container.textContent).toContain("max-age=300");
  });
  it("purge", () => {
    const fn = vi.fn();
    const { container } = render(
      <CacheControlInspector headers={headers} hitRate={90} onPurge={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Purge Cache")!);
    expect(fn).toHaveBeenCalled();
  });
});
