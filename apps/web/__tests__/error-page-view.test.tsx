import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorPageView } from "@/components/error-page-view";

describe("ErrorPageView", () => {
  it("renders 404 page", () => {
    const { container } = render(
      <ErrorPageView statusCode={404} title="Not Found" icon="🔍"
        description="Page doesn't exist" suggestions={["Check URL", "Go home"]} requestId="req_abc" />
    );
    expect(container.textContent).toContain("404");
    expect(container.textContent).toContain("Not Found");
    expect(container.textContent).toContain("🔍");
    expect(container.textContent).toContain("Check URL");
    expect(container.textContent).toContain("req_abc");
  });
});
