import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CacheConfig } from "@/components/cache-config";

describe("CacheConfig", () => {
  it("renders cache headers", () => {
    const { container } = render(
      <CacheConfig cacheControl="public, max-age=3600" directives={["public", "max-age=3600"]}
        cacheable={true} etag='W/"abc123"' />
    );
    expect(container.textContent).toContain("public, max-age=3600");
    expect(container.textContent).toContain("Cacheable");
    expect(container.textContent).toContain("abc123");
  });
});
