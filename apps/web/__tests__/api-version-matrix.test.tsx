import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiVersionMatrix } from "@/components/api-version-matrix";

describe("ApiVersionMatrix", () => {
  const versions = [
    { version: "v3", status: "active" },
    { version: "v2", status: "deprecated", sunset_date: "2027-01-01T00:00:00" },
    { version: "v1", status: "sunset" },
  ];
  it("renders", () => {
    const { container } = render(
      <ApiVersionMatrix versions={versions} latestVersion="v3" onDeprecate={vi.fn()} />
    );
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("Latest: v3");
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("Deprecated");
    expect(container.textContent).toContain("Sunset");
    expect(container.textContent).toContain("2027-01-01");
  });
});
