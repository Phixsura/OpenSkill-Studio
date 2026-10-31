import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogSubCard from "../src/components/api-developer-platform-sdk-consumer-api-changelog-sub-card";

describe("ChangelogSubCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<ChangelogSubCard />);
    expect(container.textContent).toContain("Changelog Subscribers");
    expect(container.textContent).toContain("38");
    expect(container.textContent).toContain("Active Subscribers");
  });

  it("shows recent notifications", () => {
    const { container } = render(<ChangelogSubCard />);
    expect(container.textContent).toContain("Batch API");
    expect(container.textContent).toContain("156 notifications sent");
  });
});
