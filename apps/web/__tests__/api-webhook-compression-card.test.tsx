import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookCompressionCard from "../src/components/api-webhook-compression-card";

const configs = [{ destination: "https://a.com", algorithm: "gzip", bytes_saved: 50000 }];

describe("APIWebhookCompressionCard", () => {
  it("renders with savings", () => {
    const { container } = render(<APIWebhookCompressionCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("Compression");
    expect(container.textContent).toContain("48.8KB saved");
    expect(container.textContent).toContain("gzip");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookCompressionCard configs={[]} appName="App" />);
    expect(container.textContent).toContain("No compression configs");
  });
});
