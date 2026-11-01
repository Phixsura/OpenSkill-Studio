import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorPageTemplate } from "@/components/error-page-template";

describe("ErrorPageTemplate", () => {
  it("renders error page", () => {
    const { container } = render(
      <ErrorPageTemplate code={404} title="Not Found" icon="🔍"
        message="Page doesn't exist" appName="OpenSkill" requestId="req_abc"
        actions={[{ label: "Go Home", href: "/", primary: true }]} />
    );
    expect(container.textContent).toContain("404");
    expect(container.textContent).toContain("Not Found");
    expect(container.textContent).toContain("🔍");
    expect(container.textContent).toContain("req_abc");
    expect(container.textContent).toContain("Go Home");
    expect(container.textContent).toContain("OpenSkill");
  });
});
