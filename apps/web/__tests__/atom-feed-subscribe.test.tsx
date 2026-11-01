import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AtomFeedSubscribe } from "@/components/atom-feed-subscribe";

describe("AtomFeedSubscribe", () => {
  it("renders subscribe", () => {
    const { container } = render(
      <AtomFeedSubscribe feedUrl="https://marketplace.openskill.io/apps/myapp/changelog.atom"
        appName="My App" itemCount={15} />
    );
    expect(container.textContent).toContain("Subscribe to My App Changelog");
    expect(container.textContent).toContain("15 releases");
    expect(container.textContent).toContain("Copy");
  });
});
