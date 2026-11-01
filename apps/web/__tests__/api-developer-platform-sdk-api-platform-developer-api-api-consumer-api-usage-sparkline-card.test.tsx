import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-usage-sparkline-card";

describe("UsageSparklineCard", () => {
  it("shows sparklines", () => {
    const sparklines = [{ consumer_id: "c1", metric: "requests", points: [100, 120, 150, 130, 160], trend: "up", current: 160 }];
    const { container } = render(<Card sparklines={sparklines} appName="App" />);
    expect(container.textContent).toContain("Usage Sparklines");
    expect(container.textContent).toContain("c1 / requests");
    expect(container.textContent).toContain("160");
  });
  it("shows empty", () => {
    const { container } = render(<Card sparklines={[]} appName="App" />);
    expect(container.textContent).toContain("No sparkline data");
  });
});
