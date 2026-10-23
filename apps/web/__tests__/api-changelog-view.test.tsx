import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiChangelogView } from "@/components/api-changelog-view";

describe("ApiChangelogView", () => {
  const sections = [
    { type: "added", label: "Added", icon: "➕",
      entries: [{ endpoint: "GET /users", description: "New endpoint", icon: "➕", label: "Added" }] },
    { type: "removed", label: "Removed", icon: "❌",
      entries: [{ endpoint: "GET /v1/users", description: "Deprecated", icon: "❌", label: "Removed" }] },
  ];
  it("renders", () => {
    const { container } = render(
      <ApiChangelogView version="v2" sections={sections} totalChanges={2} hasBreaking={true} />
    );
    expect(container.textContent).toContain("API Changelog — v2");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("➕");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("❌");
  });
});
