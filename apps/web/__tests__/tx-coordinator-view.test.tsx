import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TxCoordinatorView } from "@/components/tx-coordinator-view";

describe("TxCoordinatorView", () => {
  it("renders transactions", () => {
    const { container } = render(
      <TxCoordinatorView committed={5} aborted={1} successRate={83}
        transactions={[
          { txId: "tx_abc", participants: ["order", "payment"], status: "committed", votesReceived: 2 },
          { txId: "tx_def", participants: ["a", "b"], status: "aborted", votesReceived: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Transactions");
    expect(container.textContent).toContain("5 committed");
    expect(container.textContent).toContain("1 aborted");
    expect(container.textContent).toContain("83%");
    expect(container.textContent).toContain("tx_abc");
    expect(container.textContent).toContain("order, payment");
  });
});
