import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CacheInvalidatorCard from "../src/components/api-developer-platform-sdk-consumer-api-cache-invalidator-card";

describe("CacheInvalidatorCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<CacheInvalidatorCard />);
    expect(container.textContent).toContain("Cache Invalidator");
    expect(container.textContent).toContain("Entries");
    expect(container.textContent).toContain("35");
  });

  it("shows tags and cascade info", () => {
    const { container } = render(<CacheInvalidatorCard />);
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("orders");
    expect(container.textContent).toContain("8 cascade rules");
  });
});
