import time
import logging
from typing import Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class OpenTelemetryTracer:
    """
    OpenTelemetry Distributed Tracer: Measures span execution times across request lifecycle.
    """
    def __init__(self):
        self.spans: List[Dict[str, Any]] = []

    @contextmanager
    def start_span(self, name: str):
        start_time = time.time()
        span_id = f"span_{len(self.spans) + 1}"
        logger.info(f"OpenTelemetry Span STARTED: [{name}] ({span_id})")
        try:
            yield span_id
        finally:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            span_data = {
                "span_id": span_id,
                "name": name,
                "duration_ms": duration_ms
            }
            self.spans.append(span_data)
            logger.info(f"OpenTelemetry Span FINISHED: [{name}] in {duration_ms}ms")

tracer = OpenTelemetryTracer()
