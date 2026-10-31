import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ActivityFeedCard from "../src/components/api-developer-platform-sdk-consumer-api-activity-feed-card";

describe("ActivityFeedCard", () => {
  it("renders title and activities", () => {
    const { container } = render(<ActivityFeedCard />);
    expect(container.textContent).toContain("Activity Feed");
    expect(container.textContent).toContain("Created API key prod-key");
    expect(container.textContent).toContain("Error rate exceeded 5%");
  });

  it("shows unread badge", () => {
    const { container } = render(<ActivityFeedCard />);
    expect(container.textContent).toContain("2 new");
  });
});
