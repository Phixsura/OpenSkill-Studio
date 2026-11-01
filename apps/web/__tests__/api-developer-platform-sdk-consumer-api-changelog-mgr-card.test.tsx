import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogManagerCard from "../src/components/api-developer-platform-sdk-consumer-api-changelog-mgr-card";

describe("ChangelogManagerCard", () => {
  it("renders title and versions", () => {
    const { container } = render(<ChangelogManagerCard />);
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("v2.0.0");
  });

  it("shows entries and breaking changes", () => {
    const { container } = render(<ChangelogManagerCard />);
    expect(container.textContent).toContain("Batch API support");
    expect(container.textContent).toContain("BREAKING");
    expect(container.textContent).toContain("2 versions documented");
  });
});
