import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ContentNegotiationCard from "../src/components/content-negotiation-card";

const formats = [
  { media_type: "application/json", quality: 1.0, charset: "utf-8" },
  { media_type: "application/xml", quality: 0.8, charset: "utf-8" },
  { media_type: "text/csv", quality: 0.5, charset: "utf-8" },
];

describe("ContentNegotiationCard", () => {
  it("renders header and count", () => {
    const { container } = render(
      <ContentNegotiationCard formats={formats} defaultFormat="application/json" appName="App" />,
    );
    expect(container.textContent).toContain("Content Negotiation");
    expect(container.textContent).toContain("3 formats");
  });

  it("shows media types", () => {
    const { container } = render(
      <ContentNegotiationCard formats={formats} defaultFormat="application/json" appName="App" />,
    );
    expect(container.textContent).toContain("application/json");
    expect(container.textContent).toContain("application/xml");
    expect(container.textContent).toContain("text/csv");
  });

  it("shows default badge", () => {
    const { container } = render(
      <ContentNegotiationCard formats={formats} defaultFormat="application/json" appName="App" />,
    );
    expect(container.textContent).toContain("default");
  });

  it("shows quality and charset", () => {
    const { container } = render(
      <ContentNegotiationCard formats={formats} defaultFormat="application/json" appName="App" />,
    );
    expect(container.textContent).toContain("q=0.8");
    expect(container.textContent).toContain("utf-8");
  });

  it("shows empty state", () => {
    const { container } = render(
      <ContentNegotiationCard formats={[]} defaultFormat="" appName="App" />,
    );
    expect(container.textContent).toContain("No formats registered");
  });
});
