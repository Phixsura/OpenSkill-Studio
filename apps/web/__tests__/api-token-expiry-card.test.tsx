import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APITokenExpiryCard from "../src/components/api-token-expiry-card";

const tokens = [
  { token_id: "t1", label: "Prod Key", days_remaining: 7, is_expired: false },
  { token_id: "t2", label: "Old Key", days_remaining: 0, is_expired: true },
];

describe("APITokenExpiryCard", () => {
  it("renders alerts", () => {
    const { container } = render(<APITokenExpiryCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("1 expired");
    expect(container.textContent).toContain("1 expiring soon");
  });

  it("shows tokens", () => {
    const { container } = render(<APITokenExpiryCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("Prod Key");
    expect(container.textContent).toContain("7d left");
    expect(container.textContent).toContain("expired");
  });

  it("shows empty state", () => {
    const { container } = render(<APITokenExpiryCard tokens={[]} appName="App" />);
    expect(container.textContent).toContain("No tokens tracked");
  });
});
