import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogCard from "../src/components/api-changelog-card";

const changes = [
  {
    method: "GET",
    path: "/api/v2/users",
    change_type: "added" as const,
    breaking: false,
    description: "",
  },
  {
    method: "DELETE",
    path: "/api/v1/users",
    change_type: "removed" as const,
    breaking: true,
    description: "",
  },
];

describe("APIChangelogCard", () => {
  it("renders header", () => {
    const { container } = render(
      <APIChangelogCard fromVersion="1.0" toVersion="2.0" changes={changes} appName="My App" />,
    );
    expect(container.textContent).toContain("API Changes");
  });

  it("shows version range", () => {
    const { container } = render(
      <APIChangelogCard fromVersion="1.0" toVersion="2.0" changes={changes} appName="App" />,
    );
    expect(container.textContent).toContain("1.0 → 2.0");
  });

  it("shows breaking badge", () => {
    const { container } = render(
      <APIChangelogCard fromVersion="1.0" toVersion="2.0" changes={changes} appName="App" />,
    );
    expect(container.textContent).toContain("1 breaking");
  });

  it("renders methods and paths", () => {
    const { container } = render(
      <APIChangelogCard fromVersion="1.0" toVersion="2.0" changes={changes} appName="App" />,
    );
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v2/users");
    expect(container.textContent).toContain("DELETE");
  });

  it("shows change type icons", () => {
    const { container } = render(
      <APIChangelogCard fromVersion="1.0" toVersion="2.0" changes={changes} appName="App" />,
    );
    expect(container.textContent).toContain("+");
    expect(container.textContent).toContain("−");
  });

  it("shows empty state", () => {
    const { container } = render(
      <APIChangelogCard fromVersion="1.0" toVersion="2.0" changes={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No endpoint changes");
  });
});
