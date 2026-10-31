import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-credit-system-card";

describe("ConsumerApiCreditSystemCard", () => {
  it("shows credits", () => {
    const txs = [{ id: "t1", amount: 100, balance: 100, reason: "Purchase", timestamp: "12:00" }, { id: "t2", amount: -25, balance: 75, reason: "API call", timestamp: "12:05" }];
    const { container } = render(<Card balance={75} totalPurchased={100} totalConsumed={25} transactions={txs} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("API Credits");
    expect(container.textContent).toContain("75");
    expect(container.textContent).toContain("+100");
    expect(container.textContent).toContain("Purchase");
    expect(container.textContent).toContain("-25");
  });
  it("shows zero balance", () => {
    const { container } = render(<Card balance={0} totalPurchased={0} totalConsumed={0} transactions={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("0");
  });
});
