import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiConsumerEngagementScoreCard from "../src/components/api-developer-api-api-consumer-engagement-score-card";

const scores = [
  { consumer_id: "acme", score: 90, tier: "champion", api_call_frequency: 200, endpoint_diversity: 15 },
  { consumer_id: "beta", score: 25, tier: "casual", api_call_frequency: 2, endpoint_diversity: 1 },
];

describe("APIDeveloperAPIApiConsumerEngagementScoreCard", () => {
  it("shows engagement scores", () => {
    const { container } = render(<APIDeveloperAPIApiConsumerEngagementScoreCard scores={scores} tierBreakdown={{ champion: 1, casual: 1 }} appName="App" />);
    expect(container.textContent).toContain("Engagement Scores");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("90");
    expect(container.textContent).toContain("champion");
    expect(container.textContent).toContain("casual: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiConsumerEngagementScoreCard scores={[]} tierBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("No engagement data");
  });
});
