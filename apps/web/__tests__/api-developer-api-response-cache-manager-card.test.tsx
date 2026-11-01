import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIResponseCacheManagerCard from "../src/components/api-developer-api-response-cache-manager-card";

describe("APIDeveloperAPIResponseCacheManagerCard", () => {
  it("shows cache stats", () => {
    const { container } = render(<APIDeveloperAPIResponseCacheManagerCard stats={{ total_entries: 50, hits: 8000, misses: 2000, hit_rate_pct: 80, total_bytes: 524288 }} appName="App" />);
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("8,000");
    expect(container.textContent).toContain("512.0KB");
  });
});
