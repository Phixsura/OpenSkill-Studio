import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SharePageLayout } from "@/components/share-page-layout";

describe("SharePageLayout", () => {
  it("renders", () => {
    const { container } = render(
      <SharePageLayout appName="SuperApp" appUrl="https://openskill.dev/apps/super-app"
        twitterUrl="https://twitter.com/intent/tweet" linkedinUrl="https://linkedin.com/share"
        badgeCode="<img />" buttonCode="<a>Install</a>" qrUrl="/qr.png" />
    );
    expect(container.textContent).toContain("Share SuperApp");
    expect(container.textContent).toContain("Twitter");
    expect(container.textContent).toContain("LinkedIn");
    expect(container.textContent).toContain("Copy");
  });
});
