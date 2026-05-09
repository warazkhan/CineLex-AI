import time
from dataclasses import dataclass, field


@dataclass
class TraceContext:
    query: str
    route: str = None
    start_time: float = field(default_factory=time.time)
    node_times: dict = field(default_factory=dict)
    tool: str = None

    def start_node(self, node_name: str):
        self.node_times[node_name] = time.time()

    def end_node(self, node_name: str):
        if node_name in self.node_times:
            self.node_times[node_name] = time.time() - self.node_times[node_name]

    def latency(self):
        return time.time() - self.start_time