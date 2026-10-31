import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResponseCacheCard from "../src/components/api-developer-platform-sdk-consumer-api-response-cache-card";

describe("ResponseCacheCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<ResponseCacheCard />);
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("87.3%");
    expect(container.textContent).toContain("847");
  });

  it("shows hit and miss counts", () => {
    const { container } = render(<ResponseCacheCard />);
    expect(container.textContent).toContain("45,200 hits");
    expect(container.textContent).toContain("6,580 misses");
  });
});
