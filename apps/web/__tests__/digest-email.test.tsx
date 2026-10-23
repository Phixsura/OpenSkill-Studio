import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DigestEmail } from "@/components/digest-email";

describe("DigestEmail", () => {
  const sections = [{
    type: "install", count: 3,
    items: [{ title: "App installed", description: "" }, { title: "Another install", description: "" }],
    hasMore: true,
  }];
  it("renders digest", () => {
    const { container } = render(
      <DigestEmail subject="Weekly digest — 5 updates" period="weekly" sections={sections} totalEvents={5} />
    );
    expect(container.textContent).toContain("Weekly digest");
    expect(container.textContent).toContain("install (3)");
    expect(container.textContent).toContain("App installed");
    expect(container.textContent).toContain("+ 1 more");
  });
});
