# MaxSafe Thermal Hybrid Architecture

Pocket AI 11.0 aims for the highest sustainable answer quality on Android rather than the highest momentary CPU load.

## Operating rules

● Android thermal protection is never disabled or bypassed.

● At least one logical CPU core is left available to Android and Termux; the local runner is capped at six inference threads.

● Sensor readings are grouped into battery, skin/surface, and SoC/silicon classes because their safe ranges differ. Missing or unreliable sensors cause conservative fallback behavior.

● The governor checks live temperature and free RAM approximately every two seconds during local generation. It reduces work before the next call and stops the current pass only at emergency heat, critical heat with a rapid rise, critical RAM pressure, or the global answer deadline.

● Optional hybrid fusion is sequential. A compact analyst is unloaded before the stronger synthesizer starts, avoiding simultaneous model working sets.

## Model matching

The router combines installed-model availability with total RAM, current available RAM, processor score, task complexity, thermal level, battery state, and model-file size. The largest model is not selected when its estimated weights, KV cache, and compute buffers would consume the protected Android reserve.

## Fusion path

1. Retrieval, exact tools, school knowledge, web evidence, and conversation context are prepared once.
2. A compact safe model creates structured analysis for a difficult query.
3. The model process exits. Pocket AI checks heat, RAM, time, and applies a short cooldown when useful.
4. The strongest safe model synthesizes one natural final answer and corrects conflicts.
5. The answer auditor can keep the first result if the second pass clearly regresses.

## Limits

Thermal sensors and device cooling vary. The system proactively reduces load but cannot guarantee a device will never become warm or that every manufacturer sensor is exposed to Termux. The bundled 135M models remain emergency tiers; larger Qwen3 models provide the meaningful language/reasoning improvement.

## Adaptive compute learning

Pocket AI 12.0 records local per-model throughput, elapsed time, temperature rise, and guarded aborts. Stable cool runs can earn modest burst headroom; rapid heating or failures reduce later budgets. A final hard thermal/RAM check always runs after learned tuning.

## Guarded final critic

Difficult Qwen3 answers can receive one short final audit only while the device remains cool or normal, the model's free-RAM requirement is met, and at least 16 seconds remain.
