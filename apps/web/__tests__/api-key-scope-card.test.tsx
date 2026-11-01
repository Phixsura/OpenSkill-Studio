import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIKeyScopeCard from "../src/components/api-key-scope-card";

const keys = [
  {
    key_id: "k1",
    prefix: "abc12345",
    scopes: ["read:data", "write:data"],
    label: "Prod",
    active: true,
    request_count: 500,
  },
  {
    key_id: "k2",
    prefix: "xyz98765",
    scopes: ["read:data"],
    label: "",
    active: false,
    request_count: 10,
  },
];

describe("APIKeyScopeCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<APIKeyScopeCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("Scoped API Keys");
    expect(container.textContent).toContain("1/2 active");
  });

  it("shows key prefixes and labels", () => {
    const { container } = render(<APIKeyScopeCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("abc12345...");
    expect(container.textContent).toContain("Prod");
  });

  it("shows scope chips", () => {
    const { container } = render(<APIKeyScopeCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("read:data");
    expect(container.textContent).toContain("write:data");
  });

  it("shows empty state", () => {
    const { container } = render(<APIKeyScopeCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No scoped keys");
  });
});
