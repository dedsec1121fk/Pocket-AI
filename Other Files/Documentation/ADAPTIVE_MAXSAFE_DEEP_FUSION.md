# Adaptive MaxSafe Deep Fusion

Pocket AI 12.0 learns a safe performance envelope for each installed GGUF model on the current phone. It stores only local runtime telemetry: completed and aborted runs, approximate output characters per second, elapsed time, temperature rise, threads, context, and batch size.

## Quality path

1. Retrieval, exact tools, school knowledge, web evidence, and conversation context are assembled first.
2. The strongest model that fits live RAM, CPU, thermal, and storage constraints is selected.
3. Difficult tasks may use a compact analyst followed by the strongest safe synthesizer. Only one GGUF process is loaded at a time.
4. When a Qwen3 answer is difficult and the device remains cool, a short final critic can check completeness, commands, mathematics, comparisons, and causal claims.
5. Every stage shares the 112-second answer deadline and can be skipped or stopped by the thermal/RAM governor.

## Safe limit use

A stable cool phone may receive a modest context, batch, output, or thread increase. The hard governor then recomputes the working set and removes the burst if it would spend Android's reserved RAM. Historical rapid heating or aborted runs automatically make later plans more conservative.

Pocket AI does not overclock, change voltage, disable thermal throttling, bypass Android protections, or promise that a phone will never become warm. Hardware condition and sensor accuracy vary.
