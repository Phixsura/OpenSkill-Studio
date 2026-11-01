import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TagManagerCard from "../src/components/api-developer-platform-sdk-consumer-api-tag-manager-card";

describe("TagManagerCard", () => {
  it("renders title and tags", () => {
    const { container } = render(<TagManagerCard />);
    expect(container.textContent).toContain("Tag Manager");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("billing");
    expect(container.textContent).toContain("deprecated");
  });

  it("shows counts", () => {
    const { container } = render(<TagManagerCard />);
    expect(container.textContent).toContain("5 tags");
    expect(container.textContent).toContain("31 total assignments");
  });
});
