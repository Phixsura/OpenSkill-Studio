import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GqlSchemaViewer } from "@/components/gql-schema-viewer";

describe("GqlSchemaViewer", () => {
  it("renders schema versions", () => {
    const { container } = render(
      <GqlSchemaViewer name="API" latestVersion="2.0" totalVersions={2}
        versions={[
          { version: "2.0", hash: "abc123def456", typeCount: 15, sdlLength: 2400 },
          { version: "1.0", hash: "xyz789abc012", typeCount: 10, sdlLength: 1800 },
        ]} />
    );
    expect(container.textContent).toContain("API Schema");
    expect(container.textContent).toContain("2 versions");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("15 types");
    expect(container.textContent).toContain("abc123def456");
  });
});
