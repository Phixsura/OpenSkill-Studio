import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SharePreviewCard } from "@/components/share-preview-card";

describe("SharePreviewCard", () => {
  it("renders preview", () => {
    const { container } = render(
      <SharePreviewCard title="Slack Bot — OpenSkill" description="Best integration"
        url="https://marketplace.openskill.io/apps/slack-bot"
        image="" twitterLink="https://twitter.com/intent/tweet" linkedinLink="https://linkedin.com/share" />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Best integration");
    expect(container.textContent).toContain("Twitter");
    expect(container.textContent).toContain("LinkedIn");
    expect(container.textContent).toContain("Copy");
  });
});
