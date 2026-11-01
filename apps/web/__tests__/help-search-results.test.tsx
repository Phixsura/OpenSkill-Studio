import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HelpSearchResults } from "@/components/help-search-results";

describe("HelpSearchResults", () => {
  it("renders results", () => {
    const { container } = render(
      <HelpSearchResults query="webhook" total={1} results={[
        { title: "Getting Started with Webhooks", snippet: "Learn how to set up", url: "/help/webhooks", category: "guides" },
      ]} />
    );
    expect(container.textContent).toContain("1 results");
    expect(container.textContent).toContain("webhook");
    expect(container.textContent).toContain("Getting Started with Webhooks");
    expect(container.textContent).toContain("Learn how to set up");
  });
});
