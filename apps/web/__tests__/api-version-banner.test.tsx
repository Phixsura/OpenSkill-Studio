import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiVersionBanner } from "@/components/api-version-banner";

describe("ApiVersionBanner", () => {
  it("renders deprecated", () => {
    const { container } = render(
      <ApiVersionBanner version="v1" latest={false} deprecated={true}
        warning="v1 is deprecated — migrate to v3" />
    );
    expect(container.textContent).toContain("Deprecated");
    expect(container.textContent).toContain("migrate to v3");
  });

  it("hides for latest", () => {
    const { container } = render(
      <ApiVersionBanner version="v3" latest={true} deprecated={false} warning={null} />
    );
    expect(container.textContent).toBe("");
  });
});
