import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-payload-compressor-card";

describe("PayloadCompressorCard", () => {
  it("shows savings", () => {
    const savings = { total_original_kb: 1024, total_compressed_kb: 256, saved_kb: 768, savings_pct: 75, count: 5000 };
    const { container } = render(<Card savings={savings} algorithm="gzip" appName="App" />);
    expect(container.textContent).toContain("Payload Compressor");
    expect(container.textContent).toContain("75% saved");
    expect(container.textContent).toContain("1024 KB");
    expect(container.textContent).toContain("5,000");
  });
  it("shows algorithm", () => {
    const savings = { total_original_kb: 0, total_compressed_kb: 0, saved_kb: 0, savings_pct: 0, count: 0 };
    const { container } = render(<Card savings={savings} algorithm="deflate" appName="App" />);
    expect(container.textContent).toContain("deflate");
  });
});
