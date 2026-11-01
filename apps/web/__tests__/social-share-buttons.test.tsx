import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SocialShareButtons } from "@/components/social-share-buttons";

describe("SocialShareButtons", () => {
  it("renders", () => {
    const { container } = render(
      <SocialShareButtons url="https://example.com/app" title="Auth SDK"
        description="Best auth solution" />
    );
    expect(container.textContent).toContain("Share:");
    const links = container.querySelectorAll("a");
    expect(links.length).toBe(4);
    expect(links[0].getAttribute("href")).toContain("twitter.com");
    expect(links[1].getAttribute("href")).toContain("linkedin.com");
    expect(links[0].getAttribute("rel")).toContain("noopener");
  });
});
