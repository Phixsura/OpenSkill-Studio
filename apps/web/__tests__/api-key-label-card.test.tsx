import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIKeyLabelCard from "../src/components/api-key-label-card";

const keys = [
  { key_id: "k1", name: "Prod Key", labels: ["production", "api"] },
  { key_id: "k2", name: "Test Key", labels: ["staging"] },
];

describe("APIKeyLabelCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIKeyLabelCard keys={keys} allLabels={["api", "production", "staging"]} appName="App" />);
    expect(container.textContent).toContain("Key Labels");
    expect(container.textContent).toContain("2 keys");
    expect(container.textContent).toContain("3 labels");
  });

  it("shows key names and labels", () => {
    const { container } = render(<APIKeyLabelCard keys={keys} allLabels={[]} appName="App" />);
    expect(container.textContent).toContain("Prod Key");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("staging");
  });

  it("shows empty state", () => {
    const { container } = render(<APIKeyLabelCard keys={[]} allLabels={[]} appName="App" />);
    expect(container.textContent).toContain("No labeled keys");
  });
});
