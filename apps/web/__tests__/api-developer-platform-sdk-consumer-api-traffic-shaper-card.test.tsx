import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TrafficShaperCard from "../src/components/api-developer-platform-sdk-consumer-api-traffic-shaper-card";

describe("TrafficShaperCard", () => {
  it("renders title and lanes", () => {
    const { container } = render(<TrafficShaperCard />);
    expect(container.textContent).toContain("Traffic Shaper");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("normal");
    expect(container.textContent).toContain("background");
  });

  it("shows global RPS", () => {
    const { container } = render(<TrafficShaperCard />);
    expect(container.textContent).toContain("4,500/10,000 RPS");
  });
});
