import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContentHashPanel } from "@/components/content-hash-panel";

describe("ContentHashPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ContentHashPanel passed={2} failed={1} allValid={false}
        results={[
          { name: "config.json", match: true },
          { name: "app.js", match: true },
          { name: "data.csv", match: false },
        ]} />
    );
    expect(container.textContent).toContain("Content Integrity");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("3 checked");
    expect(container.textContent).toContain("config.json");
    expect(container.textContent).toContain("data.csv");
  });
});
