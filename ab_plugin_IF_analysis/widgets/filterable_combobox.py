# widgets/filterable_combobox.py
from PySide2.QtWidgets import QComboBox, QCompleter
from PySide2.QtCore import QStringListModel, Qt, Signal

class FilterableComboBox(QComboBox):
    selection_validated = Signal(str)  # Signal personnalisé

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)

        self.completer = QCompleter(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)

        self._all_items = items if items else []
        self._model = QStringListModel(self._all_items)
        self.completer.setModel(self._model)

        self.lineEdit().textEdited.connect(self._filter_items)
        if items:
            self.addItems(items)

    def _filter_items(self, text):
        if not text:
            self._model.setStringList(self._all_items)
        else:
            filtered_items = [item for item in self._all_items if text.lower() in item.lower()]
            self._model.setStringList(filtered_items)
        self.completer.complete()

    def set_items(self, items):
        self._all_items = items
        self.clear()
        self.addItems(items)
        self._model.setStringList(items)

    def current_text(self):
        return self.currentText()

    def focusOutEvent(self, event):
        self._validate_selection()
        super().focusOutEvent(event)

    def event(self, event):
        if event.type() == event.KeyPress and event.key() == Qt.Key_Return:
            self._validate_selection()
            return True
        return super().event(event)

    def _validate_selection(self):
        text = self.currentText()
        if text in self._all_items:
            index = self.findText(text)
            if index >= 0:
                self.setCurrentIndex(index)
            self.selection_validated.emit(text)
        else:
            self.setCurrentText("")

    def showPopup(self):
        super().showPopup()
        self._filter_items(self.lineEdit().text())
