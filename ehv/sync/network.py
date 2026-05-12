class NetworkSimulator:
    """
    Simulates a network of EHV nodes.
    Supports network partitions and eventually consistent CRDT recovery.
    """
    def __init__(self):
        self.nodes = {} # node_id -> PolicyStore
        self.state = "CONNECTED"
        self._queued_merges = [] # (source_id, target_id)

    def register_node(self, node):
        self.nodes[node.node_id] = node

    def partition(self):
        """Simulates a network partition. Updates will not propagate."""
        self.state = "PARTITIONED"
        print("[NETWORK] Partition occurred. Nodes are isolated.")

    def recover(self):
        """Simulates network recovery and processes queued merges."""
        self.state = "CONNECTED"
        print("[NETWORK] Recovery occurred. Propagating updates...")
        for source_id, target_id in self._queued_merges:
            self._do_merge(source_id, target_id)
        self._queued_merges = []

    def propagate(self, source_id, target_id):
        """Attempts to propagate policy state from source to target."""
        if self.state == "PARTITIONED":
            # Queue for later
            self._queued_merges.append((source_id, target_id))
        else:
            self._do_merge(source_id, target_id)

    def _do_merge(self, source_id, target_id):
        source = self.nodes.get(source_id)
        target = self.nodes.get(target_id)
        if source and target:
            target.merge(source)
            print(f"[SYNC] Merged state from {source_id} to {target_id}")

# Global network simulator
global_network = NetworkSimulator()
