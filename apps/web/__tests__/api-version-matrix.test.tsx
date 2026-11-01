import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiVersionMatrix } from "@/components/api-version-matrix";

describe("ApiVersionMatrix", () => {
  it("renders versions", () => {
    const { container } = render(
      <ApiVersionMatrix latest="v3" activeCount={1} deprecatedCount={1}
        versions={[
          { version: "v3", status: "active", releaseDate: "2024-10-01" },
          { version: "v2", status: "deprecated", releaseDate: "2024-01-01" },
          { version: "v1", status: "sunset", releaseDate: "2023-01-01" },
        ]} />
    );
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("1 deprecated");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("latest");
    expect(container.textContent).toContain("sunset");
  });
});
