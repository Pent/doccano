from typing import List

from pydantic import BaseModel, NonNegativeInt


class Workload(BaseModel):
    weight: NonNegativeInt
    member_id: int


class WorkloadAllocation(BaseModel):
    workloads: List[Workload]

    @property
    def member_ids(self):
        return [w.member_id for w in self.workloads]

    @property
    def weights(self):
        return [w.weight for w in self.workloads]
