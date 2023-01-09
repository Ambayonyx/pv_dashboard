from typing import Any

from data_model import Model
from view_model import ViewModel


class Control:
    def __init__(self):
        self._model_ = Model()
        self._view_ = ViewModel(self._model_)

    def load_file(self, data_file: str) -> Any:
        self._model_.create_model(data_file)
        self._view_ = ViewModel(self._model_)
        return self._view_

    def get_view(self):
        return self._view_
