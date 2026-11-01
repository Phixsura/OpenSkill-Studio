import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEndpointTagCard from "../src/components/api-endpoint-tag-card";

const tags = [
  { tag: "public", count: 5 },
  { tag: "v2", count: 3 },
  { tag: "internal", count: 2 },
];

describe("APIEndpointTagCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIEndpointTagCard tags={tags} totalEndpoints={10} appName="App" />);
    expect(container.textContent).toContain("Endpoint Tags");
    expect(container.textContent).toContain("3 tags");
    expect(container.textContent).toContain("10 endpoints");
  });

  it("shows tag chips with counts", () => {
    const { container } = render(<APIEndpointTagCard tags={tags} totalEndpoints={10} appName="App" />);
    expect(container.textContent).toContain("public");
    expect(container.textContent).toContain("5");
  });

  it("shows empty state", () => {
    const { container } = render(<APIEndpointTagCard tags={[]} totalEndpoints={0} appName="App" />);
    expect(container.textContent).toContain("No endpoint tags");
  });
});
