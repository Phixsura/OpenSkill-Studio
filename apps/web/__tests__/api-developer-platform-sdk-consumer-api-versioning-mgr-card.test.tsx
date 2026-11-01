import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import VersioningManagerCard from "../src/components/api-developer-platform-sdk-consumer-api-versioning-mgr-card";

describe("VersioningManagerCard", () => {
  it("renders title and versions", () => {
    const { container } = render(<VersioningManagerCard />);
    expect(container.textContent).toContain("API Versioning");
    expect(container.textContent).toContain("v3.0.0");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("v1.0.0");
  });

  it("shows statuses", () => {
    const { container } = render(<VersioningManagerCard />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("deprecated");
    expect(container.textContent).toContain("sunset");
    expect(container.textContent).toContain("1 active version");
  });
});
