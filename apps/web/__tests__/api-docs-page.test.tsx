import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiDocsPage } from "@/components/api-docs-page";

describe("ApiDocsPage", () => {
  it("renders", () => {
    const groups = [{
      name: "apps",
      endpoints: [{ method: "GET", path: "/apps", summary: "List apps" }],
    }];
    const { container } = render(<ApiDocsPage title="API" version="v2" groups={groups} totalEndpoints={1} />);
    expect(container.textContent).toContain("API v2");
    expect(container.textContent).toContain("/apps");
    expect(container.textContent).toContain("List apps");
  });
});
