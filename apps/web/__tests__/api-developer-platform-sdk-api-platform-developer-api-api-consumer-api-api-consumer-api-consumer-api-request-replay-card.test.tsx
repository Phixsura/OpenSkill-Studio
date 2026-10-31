import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-request-replay-card";

describe("ConsumerApiRequestReplayCard", () => {
  it("shows replays", () => {
    const replays = [{ id: "rp1", originalId: "r1", originalStatus: 200, replayStatus: 200, diffDetected: false, replayedAt: "12:00" }];
    const { container } = render(<Card replays={replays} storedCount={10} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Request Replay");
    expect(container.textContent).toContain("200 → 200");
    expect(container.textContent).toContain("OK");
    expect(container.textContent).toContain("10 stored");
  });
  it("shows empty", () => {
    const { container } = render(<Card replays={[]} storedCount={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No replays yet");
  });
});
