import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppPreviewCard } from "@/components/app-preview-card";

describe("AppPreviewCard", () => {
  it("shows all info", () => {
    const { container } = render(<AppPreviewCard name="Cool App" slug="cool-app" category="connector" description="Great connector"
      installCount={42} healthScore={95} developerName="Dev Co" verified={true} />);
    expect(container.textContent).toContain("Cool App");
    expect(container.textContent).toContain("Dev Co");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("42");
  });
  it("links to app page", () => {
    const { container } = render(<AppPreviewCard name="X" slug="my-app" category="automation" description={null}
      installCount={0} healthScore={100} developerName="D" verified={false} />);
    expect(container.querySelector("a")?.getAttribute("href")).toContain("my-app");
  });
});
