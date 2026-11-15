from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar("T")

class IBaseRepository(ABC, Generic[T]):
    """
    Interface Segregation & Liskov Substitution Principle:
    Base contract for all entity repositories.
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass
