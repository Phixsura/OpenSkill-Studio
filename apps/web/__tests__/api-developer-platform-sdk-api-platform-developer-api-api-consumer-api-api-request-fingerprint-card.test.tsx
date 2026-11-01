import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-fingerprint-card";

describe("RequestFingerprintCard", () => {
  it("shows fingerprints", () => {
    const fps = [{ fingerprint_id: "fp1", method: "GET", path: "/users", hit_count: 5000 }];
    const { container } = render(<Card fingerprints={fps} uniqueCount={50} dedupRatio={35} appName="App" />);
    expect(container.textContent).toContain("Request Fingerprints");
    expect(container.textContent).toContain("50 unique");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("35% dedup");
  });
  it("shows empty", () => {
    const { container } = render(<Card fingerprints={[]} uniqueCount={0} dedupRatio={0} appName="App" />);
    expect(container.textContent).toContain("No fingerprints");
  });
});
