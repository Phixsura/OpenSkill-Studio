import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-response-cache-card";

describe("ResponseCacheCard", () => {
  it("shows cache info", () => {
    const { container } = render(<Card cacheSize={2500} hitRate={75.5} maxEntries={5000} appName="App" />);
    expect(container.textContent).toContain("Response Cache");
    expect(container.textContent).toContain("2,500");
    expect(container.textContent).toContain("75.5% hits");
    expect(container.textContent).toContain("5,000");
  });
  it("shows zero", () => {
    const { container } = render(<Card cacheSize={0} hitRate={0} maxEntries={1000} appName="App" />);
    expect(container.textContent).toContain("0% hits");
  });
});
