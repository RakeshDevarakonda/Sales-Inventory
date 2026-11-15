from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar("T")

class IReadOnlyRepository(ABC, Generic[T]):
    """
    Interface Segregation Principle:
    Separate contract for read operations. Not every entity (e.g. Orders) allows hard deletion.
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass


class IDeletableRepository(ABC):
    """
    Interface Segregation Principle:
    Only entities that support physical deletion implement this interface.
    """

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass
