import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotFoundPage } from "@/components/not-found-page";

describe("NotFoundPage", () => {
  it("renders 404 with suggestions", () => {
    const { container } = render(
      <NotFoundPage requestedPath="/docs/start"
        suggestions={["/docs/getting-started"]} categoryMatches={[]} />
    );
    expect(container.textContent).toContain("404");
    expect(container.textContent).toContain("/docs/start");
    expect(container.textContent).toContain("Did you mean");
    expect(container.textContent).toContain("/docs/getting-started");
  });
  it("no suggestions", () => {
    const { container } = render(
      <NotFoundPage requestedPath="/xyz" suggestions={[]} categoryMatches={[]} />
    );
    expect(container.textContent).toContain("404");
    expect(container.textContent).not.toContain("Did you mean");
  });
});
