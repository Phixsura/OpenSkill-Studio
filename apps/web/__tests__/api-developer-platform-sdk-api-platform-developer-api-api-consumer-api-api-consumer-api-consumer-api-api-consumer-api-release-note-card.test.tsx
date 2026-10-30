import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-release-note-card";

describe("ConsumerApiReleaseNoteCard", () => {
  it("shows notes", () => {
    const notes = [{ id: "n1", version: "2.0", title: "OAuth2 Support", type: "feature", publishedAt: "2026-06-01" }];
    const { container } = render(<Card notes={notes} appName="App" />);
    expect(container.textContent).toContain("Release Notes");
    expect(container.textContent).toContain("OAuth2 Support");
    expect(container.textContent).toContain("v2.0");
  });
  it("shows empty", () => {
    const { container } = render(<Card notes={[]} appName="App" />);
    expect(container.textContent).toContain("No release notes");
  });
});
