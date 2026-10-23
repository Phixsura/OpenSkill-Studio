import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeepLinkGeneratorCard } from "@/components/deep-link-generator-card";

describe("DeepLinkGeneratorCard", () => {
  it("renders all links", () => {
    const { container } = render(
      <DeepLinkGeneratorCard deepLink="openskill://app/123" shortLink="https://osk.link/abc"
        webFallback="https://marketplace.openskill.dev/apps/123" qrUrl="https://api.openskill.dev/qr" />
    );
    expect(container.textContent).toContain("Deep Links");
    expect(container.textContent).toContain("openskill://app/123");
    expect(container.textContent).toContain("https://osk.link/abc");
    expect(container.textContent).toContain("Web Fallback");
    expect(container.querySelectorAll("button").length).toBe(3);
  });
});
