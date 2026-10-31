import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperKnowledgeBaseCard from "../src/components/api-developer-platform-sdk-api-developer-knowledge-base-card";

const articles = [{ article_id: "a1", title: "Auth Guide", category: "getting_started", views: 5000, helpful_votes: 200 }];

describe("Card", () => {
  it("shows knowledge base", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperKnowledgeBaseCard articles={articles} categoryCounts={{ getting_started: 5, faq: 10 }} appName="App" />);
    expect(container.textContent).toContain("Knowledge Base");
    expect(container.textContent).toContain("Auth Guide");
    expect(container.textContent).toContain("5000 views");
    expect(container.textContent).toContain("getting started: 5");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperKnowledgeBaseCard articles={[]} categoryCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No articles");
  });
});
