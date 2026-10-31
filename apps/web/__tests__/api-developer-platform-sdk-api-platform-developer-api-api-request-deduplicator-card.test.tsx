import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-request-deduplicator-card";

describe("DeduplicatorCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card stats={{ total_fingerprints: 500, duplicates_detected: 25 }} windowSeconds={5} appName="App" />);
    expect(container.textContent).toContain("Deduplicator");
    expect(container.textContent).toContain("5.0% dupes");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("25");
  });
  it("shows zero", () => {
    const { container } = render(<Card stats={{ total_fingerprints: 0, duplicates_detected: 0 }} windowSeconds={5} appName="App" />);
    expect(container.textContent).toContain("0.0% dupes");
  });
});
