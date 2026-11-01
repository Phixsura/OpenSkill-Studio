import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedbackCard from "../src/components/api-developer-platform-sdk-api-developer-api-documentation-feedback-card";

describe("Card", () => {
  it("shows doc feedback", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedbackCard totalFeedback={500} helpfulnessRate={78} worstPages={[["/docs/webhooks", 40]]} recentComments={[{ feedback_id: "f1", page_path: "/docs", helpful: true, comment: "Very helpful!" }]} appName="App" />);
    expect(container.textContent).toContain("Doc Feedback");
    expect(container.textContent).toContain("500 responses");
    expect(container.textContent).toContain("78% helpful");
    expect(container.textContent).toContain("/docs/webhooks");
    expect(container.textContent).toContain("Very helpful!");
  });
});
