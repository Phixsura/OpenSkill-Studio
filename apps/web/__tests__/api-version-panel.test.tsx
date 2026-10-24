import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiVersionPanel } from "@/components/api-version-panel";

describe("ApiVersionPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ApiVersionPanel latest="v2" total={3}
        versions={[
          { version: "v2", status: "active", sunsetDate: "" },
          { version: "v1", status: "deprecated", sunsetDate: "2027-01-01" },
        ]} />
    );
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("latest: v2");
    expect(container.textContent).toContain("3 versions");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("deprecated");
    expect(container.textContent).toContain("2027-01-01");
  });
});
