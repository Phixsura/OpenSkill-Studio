import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-decompressor-card";

describe("RequestDecompressorCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card decompressedCount={5000} totalInKb={256} totalOutKb={1024} maxSizeKb={10240} appName="App" />);
    expect(container.textContent).toContain("Request Decompressor");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("256 KB");
    expect(container.textContent).toContain("75% compression");
  });
  it("shows max size", () => {
    const { container } = render(<Card decompressedCount={0} totalInKb={0} totalOutKb={0} maxSizeKb={5120} appName="App" />);
    expect(container.textContent).toContain("max 5120 KB");
  });
});
