from PySide2.QtWidgets import QComboBox, QCompleter
from PySide2.QtCore import QStringListModel, Qt, Signal, QTimer

class FilterableComboBox(QComboBox):
    selection_validated = Signal(str)

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)

        self.completer = QCompleter(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)

        self._all_items = [item for item in (items if items else []) if item]
        self._model = QStringListModel(self._all_items)
        self.completer.setModel(self._model)

        self._last_validated_text = None

        self.lineEdit().textEdited.connect(self._filter_items)
        self.activated.connect(self._validate_selection)
        self.lineEdit().returnPressed.connect(self._validate_selection)
        if items:
            self.addItems(items)

    def _filter_items(self, text):
        if not text:
            self._model.setStringList(self._all_items)
        else:
            filtered_items = [item for item in self._all_items if item.lower().startswith(text.lower())]
            self._model.setStringList(filtered_items)
        if self.view().isVisible():  # Évite les appels redondants
            self.completer.complete()

    def set_items(self, items):
        self._all_items = [item for item in items if item]
        self.clear()
        self.addItems(items)
        self._model.setStringList(self._all_items)

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
        # Désactive temporairement le signal textEdited et le completer
        self.lineEdit().textEdited.disconnect(self._filter_items)

        text = self.currentText()
        if text in self._all_items:
            self._last_validated_text = text
            index = self.findText(text)
            if index >= 0:
                self.setCurrentIndex(index)
                self.lineEdit().setText(text)
                self.selection_validated.emit(text)
        else:
            # Si le texte n'est pas valide, on restaure la dernière valeur validée
            if self._last_validated_text is not None:
                self.lineEdit().setText(self._last_validated_text)
                self.setCurrentIndex(self.findText(self._last_validated_text))
            else:
                # Si aucune valeur n'a encore été validée, on laisse le texte vide
                self.lineEdit().setText("")
                self.setCurrentIndex(-1)

        # Ferme la popup et quitte le focus
        QTimer.singleShot(100, self.clearFocus)

        # Réactive le signal et le completer
        self.lineEdit().textEdited.connect(self._filter_items)
        QTimer.singleShot(100, lambda: self.completer.setCompletionMode(QCompleter.PopupCompletion))