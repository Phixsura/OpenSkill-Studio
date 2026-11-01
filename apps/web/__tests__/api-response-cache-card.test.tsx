import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIResponseCacheCard from "../src/components/api-response-cache-card";

describe("APIResponseCacheCard", () => {
  it("renders header and stats", () => {
    const { container } = render(<APIResponseCacheCard cacheSize={50} hitRate={85.5} totalHits={855} totalMisses={145} appName="App" />);
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("50 entries");
    expect(container.textContent).toContain("85.5%");
    expect(container.textContent).toContain("855");
    expect(container.textContent).toContain("145");
  });
});
