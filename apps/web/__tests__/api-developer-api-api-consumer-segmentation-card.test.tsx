import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiConsumerSegmentationCard from "../src/components/api-developer-api-api-consumer-segmentation-card";

const segments = [
  { segment_id: "s1", name: "Power Users", member_count: 50, criteria: { min_calls: "1000" } },
  { segment_id: "s2", name: "Enterprise", member_count: 10, criteria: {} },
];

describe("APIDeveloperAPIApiConsumerSegmentationCard", () => {
  it("shows segments", () => {
    const { container } = render(<APIDeveloperAPIApiConsumerSegmentationCard segments={segments} appName="App" />);
    expect(container.textContent).toContain("Consumer Segments");
    expect(container.textContent).toContain("2 segments");
    expect(container.textContent).toContain("60 members");
    expect(container.textContent).toContain("Power Users");
    expect(container.textContent).toContain("min_calls=1000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiConsumerSegmentationCard segments={[]} appName="App" />);
    expect(container.textContent).toContain("No segments");
  });
});
